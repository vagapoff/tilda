/**
 * JavaScript для агента транскрипции видео
 * MVP версия с основной функциональностью
 */

class TranscriptionApp {
    constructor() {
        this.apiBaseUrl = '/api/v1';
        this.currentTaskId = null;
        this.progressInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupDropZone();
        console.log('🎬 Агент транскрипции видео инициализирован');
    }
    
    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Загрузка файла
        document.getElementById('fileUploadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFileUpload();
        });
        
        // Загрузка по URL
        document.getElementById('urlUploadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleUrlUpload();
        });
        
        // Валидация URL
        document.getElementById('validateBtn').addEventListener('click', () => {
            this.validateUrl();
        });
        
        // Скачивание результата
        document.getElementById('downloadBtn').addEventListener('click', () => {
            this.downloadResult();
        });
        
        // Новая задача
        document.getElementById('newTaskBtn').addEventListener('click', () => {
            this.resetForm();
        });
        
        // Изменение URL для автоматической валидации
        document.getElementById('videoUrl').addEventListener('input', 
            this.debounce(() => this.autoValidateUrl(), 1000)
        );
    }
    
    /**
     * Настройка drag & drop зоны
     */
    setupDropZone() {
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        
        // Клик на зону
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Выбор файла
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelection(e.target.files[0]);
            }
        });
        
        // Drag & Drop события
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                this.handleFileSelection(files[0]);
            }
        });
    }
    
    /**
     * Обработка выбора файла
     */
    handleFileSelection(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        
        // Проверка типа файла
        const allowedTypes = [
            'video/mp4', 'video/avi', 'video/quicktime', 
            'video/x-msvideo', 'video/x-ms-wmv', 'video/x-flv', 'video/webm'
        ];
        
        if (!allowedTypes.includes(file.type) && !this.isVideoFile(file.name)) {
            this.showError('Неподдерживаемый формат файла. Загрузите видеофайл.');
            return;
        }
        
        // Проверка размера (2 ГБ = 2,147,483,648 байт)
        const maxSize = 2 * 1024 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('Файл слишком большой. Максимальный размер: 2 ГБ');
            return;
        }
        
        // Отображение информации о файле
        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        fileInfo.style.display = 'block';
        
        this.showSuccess(`Файл "${file.name}" выбран для загрузки`);
    }
    
    /**
     * Обработка загрузки файла
     */
    async handleFileUpload() {
        const form = document.getElementById('fileUploadForm');
        const fileInput = document.getElementById('fileInput');
        
        if (!fileInput.files.length) {
            this.showError('Выберите файл для загрузки');
            return;
        }
        
        const formData = new FormData(form);
        
        try {
            this.setLoading(true);
            this.showInfo('Загрузка файла...');
            
            const response = await fetch(`${this.apiBaseUrl}/transcribe/`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка при загрузке файла');
            }
            
            const task = await response.json();
            this.currentTaskId = task.task_id;
            
            this.showProgressSection();
            this.startProgressMonitoring();
            this.showSuccess('Файл загружен, начинается обработка...');
            
        } catch (error) {
            this.showError(`Ошибка загрузки: ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Обработка загрузки по URL
     */
    async handleUrlUpload() {
        const form = document.getElementById('urlUploadForm');
        const formData = new FormData(form);
        
        const requestData = {
            url: formData.get('url'),
            language: formData.get('language'),
            output_format: formData.get('output_format'),
            include_timestamps: formData.get('include_timestamps') === 'on',
            quality: formData.get('quality')
        };
        
        try {
            this.setLoading(true);
            this.showInfo('Создание задачи...');
            
            const response = await fetch(`${this.apiBaseUrl}/transcribe/url`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка при создании задачи');
            }
            
            const task = await response.json();
            this.currentTaskId = task.task_id;
            
            this.showProgressSection();
            this.startProgressMonitoring();
            this.showSuccess('Задача создана, начинается скачивание...');
            
        } catch (error) {
            this.showError(`Ошибка: ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Валидация URL
     */
    async validateUrl() {
        const urlInput = document.getElementById('videoUrl');
        const url = urlInput.value.trim();
        
        if (!url) {
            this.showError('Введите URL видео');
            return;
        }
        
        try {
            this.setLoading(true, 'validateBtn');
            
            const response = await fetch(`${this.apiBaseUrl}/platforms/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });
            
            const result = await response.json();
            this.displayUrlValidation(result);
            
        } catch (error) {
            this.showError(`Ошибка валидации: ${error.message}`);
        } finally {
            this.setLoading(false, 'validateBtn');
        }
    }
    
    /**
     * Автоматическая валидация URL при вводе
     */
    async autoValidateUrl() {
        const urlInput = document.getElementById('videoUrl');
        const url = urlInput.value.trim();
        
        if (url && this.isValidUrl(url)) {
            await this.validateUrl();
        }
    }
    
    /**
     * Отображение результата валидации URL
     */
    displayUrlValidation(result) {
        const container = document.getElementById('urlValidation');
        
        if (result.is_valid) {
            let content = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>URL корректен!</strong> Платформа: ${result.platform || 'Неизвестно'}
                </div>
            `;
            
            if (result.metadata) {
                content += `
                    <div class="result-metadata">
                        <h6><i class="fas fa-info-circle me-2"></i>Информация о видео</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <strong>Название:</strong> ${result.metadata.title || 'Не указано'}
                            </div>
                            <div class="col-md-6">
                                <strong>Длительность:</strong> ${this.formatDuration(result.metadata.duration)}
                            </div>
                            <div class="col-12">
                                <strong>Платформа:</strong> ${result.metadata.platform || 'Неизвестно'}
                            </div>
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = content;
        } else {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Ошибка валидации:</strong> ${result.reason || 'URL недействителен'}
                </div>
            `;
        }
        
        container.style.display = 'block';
    }
    
    /**
     * Мониторинг прогресса задачи
     */
    startProgressMonitoring() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        this.progressInterval = setInterval(() => {
            this.checkTaskProgress();
        }, 2000); // Проверка каждые 2 секунды
        
        // Первая проверка сразу
        this.checkTaskProgress();
    }
    
    /**
     * Проверка прогресса задачи
     */
    async checkTaskProgress() {
        if (!this.currentTaskId) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/transcribe/${this.currentTaskId}/status`);
            
            if (!response.ok) {
                throw new Error('Ошибка при получении статуса задачи');
            }
            
            const status = await response.json();
            this.updateProgress(status);
            
            // Если задача завершена или провалилась, останавливаем мониторинг
            if (status.status === 'completed' || status.status === 'failed') {
                this.stopProgressMonitoring();
                
                if (status.status === 'completed') {
                    await this.loadTaskResult();
                } else {
                    this.showError(`Задача провалилась: ${status.error || 'Неизвестная ошибка'}`);
                }
            }
            
        } catch (error) {
            console.error('Ошибка мониторинга прогресса:', error);
        }
    }
    
    /**
     * Обновление прогресса
     */
    updateProgress(status) {
        const progressBar = document.getElementById('progressBar');
        const progressPercent = document.getElementById('progressPercent');
        const progressLabel = document.getElementById('progressLabel');
        const taskId = document.getElementById('taskId');
        
        progressBar.style.width = `${status.progress}%`;
        progressPercent.textContent = `${Math.round(status.progress)}%`;
        progressLabel.textContent = status.message || 'Обработка...';
        taskId.textContent = status.task_id;
        
        // Изменение цвета прогресс-бара в зависимости от статуса
        progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
        
        switch (status.status) {
            case 'downloading':
                progressBar.classList.add('bg-info');
                break;
            case 'processing':
                progressBar.classList.add('bg-warning');
                break;
            case 'transcribing':
                progressBar.classList.add('bg-primary');
                break;
            case 'completed':
                progressBar.classList.add('bg-success');
                progressBar.classList.remove('progress-bar-animated');
                break;
            case 'failed':
                progressBar.classList.add('bg-danger');
                progressBar.classList.remove('progress-bar-animated');
                break;
        }
    }
    
    /**
     * Остановка мониторинга прогресса
     */
    stopProgressMonitoring() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }
    
    /**
     * Загрузка результата задачи
     */
    async loadTaskResult() {
        if (!this.currentTaskId) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/transcribe/${this.currentTaskId}/result`);
            
            if (!response.ok) {
                throw new Error('Ошибка при получении результата');
            }
            
            const task = await response.json();
            this.displayResult(task);
            
        } catch (error) {
            this.showError(`Ошибка загрузки результата: ${error.message}`);
        }
    }
    
    /**
     * Отображение результата
     */
    displayResult(task) {
        const resultContent = document.getElementById('resultContent');
        
        let content = '';
        
        // Метаданные видео (если есть)
        if (task.video_metadata) {
            content += `
                <div class="result-metadata">
                    <h6><i class="fas fa-video me-2"></i>Информация о видео</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <strong>Название:</strong> ${task.video_metadata.title || 'Не указано'}
                        </div>
                        <div class="col-md-6">
                            <strong>Длительность:</strong> ${this.formatDuration(task.video_metadata.duration)}
                        </div>
                        <div class="col-md-6">
                            <strong>Платформа:</strong> ${task.video_metadata.platform || 'Файл'}
                        </div>
                        <div class="col-md-6">
                            <strong>Язык:</strong> ${task.result.language}
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Результат транскрипции
        if (task.result) {
            content += `
                <div class="mb-3">
                    <h6><i class="fas fa-file-text me-2"></i>Текст транскрипции</h6>
                    <div class="result-text">${task.result.text}</div>
                </div>
            `;
            
            // Статистика
            content += `
                <div class="row text-center">
                    <div class="col-md-3">
                        <div class="feature-item">
                            <i class="fas fa-clock text-primary"></i>
                            <small>Время обработки<br>${task.result.processing_time || 0}с</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="feature-item">
                            <i class="fas fa-percentage text-success"></i>
                            <small>Точность<br>${Math.round((task.result.confidence || 0) * 100)}%</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="feature-item">
                            <i class="fas fa-list text-info"></i>
                            <small>Сегментов<br>${task.result.segments?.length || 0}</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="feature-item">
                            <i class="fas fa-language text-warning"></i>
                            <small>Язык<br>${task.result.language}</small>
                        </div>
                    </div>
                </div>
            `;
        }
        
        resultContent.innerHTML = content;
        this.showResultsSection();
        this.showSuccess('Транскрипция завершена успешно!');
    }
    
    /**
     * Скачивание результата
     */
    downloadResult() {
        if (!this.currentTaskId) {
            this.showError('Нет активной задачи для скачивания');
            return;
        }
        
        const format = document.getElementById('outputFormat').value || 
                      document.getElementById('urlOutputFormat').value || 'srt';
        
        const downloadUrl = `${this.apiBaseUrl}/transcribe/${this.currentTaskId}/download?format=${format}`;
        
        // Создание временной ссылки для скачивания
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `transcription_${this.currentTaskId}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showSuccess('Скачивание началось...');
    }
    
    /**
     * Сброс формы для новой задачи
     */
    resetForm() {
        // Остановка мониторинга
        this.stopProgressMonitoring();
        this.currentTaskId = null;
        
        // Сброс форм
        document.getElementById('fileUploadForm').reset();
        document.getElementById('urlUploadForm').reset();
        
        // Скрытие секций
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'none';
        
        // Скрытие информации о файле
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('urlValidation').style.display = 'none';
        
        // Очистка алертов
        document.getElementById('alertContainer').innerHTML = '';
        
        this.showSuccess('Готов к новой задаче');
    }
    
    /**
     * Показ секции прогресса
     */
    showProgressSection() {
        document.getElementById('progressSection').style.display = 'block';
        document.getElementById('progressSection').classList.add('fade-in');
        document.getElementById('resultsSection').style.display = 'none';
    }
    
    /**
     * Показ секции результатов
     */
    showResultsSection() {
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsSection').classList.add('fade-in');
    }
    
    /**
     * Установка состояния загрузки
     */
    setLoading(isLoading, buttonId = null) {
        const buttons = buttonId ? 
            [document.getElementById(buttonId)] : 
            [
                document.getElementById('uploadBtn'),
                document.getElementById('urlUploadBtn'),
                document.getElementById('validateBtn')
            ];
        
        buttons.forEach(btn => {
            if (btn) {
                btn.disabled = isLoading;
                
                if (isLoading) {
                    btn.innerHTML = `<span class="loading-spinner me-2"></span>Загрузка...`;
                } else {
                    // Восстановление оригинального текста
                    const originalTexts = {
                        'uploadBtn': '<i class="fas fa-play me-2"></i>Начать транскрипцию',
                        'urlUploadBtn': '<i class="fas fa-download me-2"></i>Скачать и транскрибировать',
                        'validateBtn': '<i class="fas fa-check me-2"></i>Проверить ссылку'
                    };
                    
                    btn.innerHTML = originalTexts[btn.id] || btn.innerHTML;
                }
            }
        });
    }
    
    /**
     * Показ уведомлений
     */
    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer');
        const alertId = `alert_${Date.now()}`;
        
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHtml);
        
        // Автоматическое удаление через 5 секунд
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
    
    showSuccess(message) { this.showAlert(message, 'success'); }
    showError(message) { this.showAlert(message, 'danger'); }
    showWarning(message) { this.showAlert(message, 'warning'); }
    showInfo(message) { this.showAlert(message, 'info'); }
    
    /**
     * Получение иконки для алерта
     */
    getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    /**
     * Утилиты
     */
    isVideoFile(filename) {
        const videoExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'];
        return videoExtensions.some(ext => filename.toLowerCase().endsWith(ext));
    }
    
    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Байт';
        
        const k = 1024;
        const sizes = ['Байт', 'КБ', 'МБ', 'ГБ'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatDuration(seconds) {
        if (!seconds) return 'Неизвестно';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Инициализация приложения при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.transcriptionApp = new TranscriptionApp();
});