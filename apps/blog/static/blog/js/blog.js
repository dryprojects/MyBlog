/**
 * Created by Jenne on 2018/4/2.
 */

jQuery(document).ready(function ($) {
    $('.logo').fancynav();

    $('.social-wrapper').mouseenter(function (e) {
        $(this).children('.userdetail').removeClass('hide');
        $(this).children('.userdetail').fadeIn(300);
    }).mouseleave(function (e) {

        $(this).children('.userdetail').fadeOut(300);
    });


    $('.post-body a').mouseenter(function (e) {
        $(this).children('span').removeClass('hide');
        $(this).children('span').fadeIn(300);
    }).mouseleave(function (e) {

        $(this).children('span').fadeOut(200);
    });

    $('.hot-post a').mouseenter(function (e) {
        $(this).children('span').removeClass('hide');
        $(this).children('span').fadeIn(300);
    }).mouseleave(function (e) {

        $(this).children('span').fadeOut(200);
    });

    $('.rec-blog a').mouseenter(function (e) {
        $(this).children('span').removeClass('hide');
        $(this).children('span').fadeIn(300);
    }).mouseleave(function (e) {

        $(this).children('span').fadeOut(200);
    });

    $("#tagcloud").windstagball({
        radius: 100,
        speed: 0.5
    });

    //ajax csrf settings
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    //点赞处理
    function PostThumb(settings) {
        this.__init__(settings)
    }

    PostThumb.prototype = {
        __init__: function (settings) {
            this.thumb_url = settings.thumb_url;
            this.target = $('.action-thumbs');
            this.text = $('.thumb-text');
            this.bind_events();
        },
        bind_events: function () {
            var self = this;

            $('.post-detail-actions').on('click', '.action-thumbs', function () {
                $.ajax({
                    type: 'POST',
                    url: self.thumb_url,
                    dataType: 'json',
                    success: function (data, status, xhr) {
                        self.text.text(data.n_praise);
                    },
                });
            });
        }
    };

    window.PostThumb = PostThumb;
});
