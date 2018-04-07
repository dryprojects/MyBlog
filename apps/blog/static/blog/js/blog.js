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

    var data = [
        { "value": "1", "label": "one" },
        { "value": "2", "label": "two" },
        { "value": "3", "label": "three" },
        { "value": "4", "label": "four" },
        { "value": "5", "label": "five" },
        { "value": "6", "label": "six" }
    ];
    $('#search-input').autocompleter({
        source:'http://localhost:8000',
        limit:5,
        cache:true,
        combine:function (args) {
            // 可以额外给服务器发送参数
            return {
                'q':args.query,
                'count':args.limit
            };
        },
        callback:function (value, index, object) {
            console.log(
                'Value ' + value + ' are selected (with index ' + index + ').'
            );
            console.log(object);
        }
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
