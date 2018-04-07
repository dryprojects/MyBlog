/**
 * Created by Jenne on 2018/4/2.
 */

jQuery(document).ready(function($) {
    $('.logo').fancynav();

    $('.post-excerpt a').mouseenter(function(e) {
        $(this).children('span').removeClass('hide');
        $(this).children('span').fadeIn(300);
    }).mouseleave(function(e) {

        $(this).children('span').fadeOut(200);
    });

    $('.hot-post a').mouseenter(function(e) {
        $(this).children('span').removeClass('hide');
        $(this).children('span').fadeIn(300);
    }).mouseleave(function(e) {

        $(this).children('span').fadeOut(200);
    });

    $('.rec-blog a').mouseenter(function(e) {
        $(this).children('span').removeClass('hide');
        $(this).children('span').fadeIn(300);
    }).mouseleave(function(e) {

        $(this).children('span').fadeOut(200);
    });

    $("#tagcloud").windstagball({
        radius:100,
        speed:0.5
    });

    // $.backstretch(
    //     ["images/bg/bg6.jpg", "images/bg/bg5.jpg", "images/bg/bg4.jpg", "images/bg/bg3.jpg", "images/bg/bg2.jpg"],
    //     {duration:4000}
    // );

});
