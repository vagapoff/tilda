(function($) {
    "use strict";
    $(document).ready(function(){
        $('[data-record-type="390"],[data-record-type="702"],[data-record-type="131"]').addClass('notme')
$('head').append('<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.6.3/css/all.css" integrity="sha384-UHRtZLI+pbxtHCWp1t77Bi1L4ZtiqrqD80Kn4Z8NTSRyMA2Fd33n5dQ8lWUE00s/" crossorigin="anonymous">')
$(document).ready(function(){$('[data-tilda-sign]').remove();$("img").mousedown(function(){return false;});});
if($('.t391__btn').length){
    $('.t391 .t391__btn').each(function(){
        $(this).css({'opacity':1});
        var id = $(this).find('a').attr('href')
                
        $(this).find('a').remove()
        if(id.indexOf("#rec") >= 0){
            $(id).addClass('just_as_added_button')
            $(id).find('a').parentsUntil(id).addClass('uncss_us_plz')
            $(this).append($(id))
        }
        //$(id).remove();/**/
    })
}
if($('.t390__btn-wrapper').length){
    $('.t390__btn-wrapper').each(function(){
        var id = $(this).find('a').attr('href')
        $(this).find('a').remove()
        if(id.indexOf("#rec") >= 0){
            $(id).addClass('just_as_added_button')
            $(id).find('a').parentsUntil(id).addClass('uncss_us_plz')
            $(this).append($(id))
        }
        //$(id).remove();/**/
    })
}

var widther = $('.t228__leftcontainer a').width()
$('.t228__right_descr').css({'margin-left':widther+'px'})
$('.t228__leftcontainer').append('<div class="th_wrp"><div class="th_out"><div class="th_in">')
$('.t228__leftcontainer .th_in').append($('.t228__right_descr'))
function addGoogleFont(FontName) {
    $("head").append("<link href='https://fonts.googleapis.com/css?family=" + FontName + ":400,500,600,700' rel='stylesheet' type='text/css'>");
}

addGoogleFont("Montserrat"); // for example

    });
})(jQuery);
