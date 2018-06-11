$(function () {
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

    // key, image_url, audio_url

    function SimpleCaptcha(settings) {
        this.__init__(settings);
    }

    SimpleCaptcha.prototype = {
        __init__: function (settings) {
            this.captcha_refresh_url = settings.captcha_refresh_url;
            this.$captcha = $('.captcha');
            this.$captcha_input = $('#id_captcha_0');

            this.bind_captcha_events();
        },
        bind_captcha_events: function () {
            var self = this;

            $('.form-widgets').on('click', '.captcha', function () {
                $.get(self.captcha_refresh_url, function (data) {
                    self.$captcha.attr('src', data.image_url);
                    self.$captcha_input.val(data.key)
                });
            });
        },
    };

    window.SimpleCaptcha = SimpleCaptcha;
});