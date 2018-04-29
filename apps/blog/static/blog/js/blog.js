/**
 * Created by Jenne on 2018/4/2.
 */

jQuery(document).ready(function ($) {
    $('.logo').fancynav();

    $('.post-excerpt a').mouseenter(function (e) {
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

    // Comment
    function MyBlogComment(settings) {
        var username = $('#username').val();
        $('.comment-caution').text(' 文明留言， 说说你的看法。 当前登陆用户：' + username);
        this.__init__(settings);
    }

    MyBlogComment.prototype = {
        __init__: function (settings) {
            this.$textarea = $(settings.textarea);
            this.comment_template = '           <li id="comment{{COMMENT_ID}}" class="post-comment">\n' +
                '                                <table>\n' +
                '                                    <tr>\n' +
                '                                        <td class="comment-user col-md-1">\n' +
                '                                            <img src="{{USER_IMAGE}}" alt="" class="comment-avatar">\n' +
                '                                        </td>\n' +
                '                                        <td class="post-comment-body col-md-11">\n' +
                '                                            {{COMMENT}}\n' +
                '                                            <ul class="post-comment-meta">\n' +
                '                                                <li><span class="far fa-thumbs-up comment-like{{COMMENT_ID}}"> 赞({{COMMENT_N_LIKE}})</span></li>\n' +
                '                                                <li>|</li>\n' +
                '                                                <li><span class="comment{{COMMENT_ID}}">回复</span></li>\n' +
                '                                                <li><span class="comment-remove{{COMMENT_ID}}">删除</span></li>\n' +
                '                                                <li class="post-comment-date pull-left"><span class="comment-name{{COMMENT_ID}}">{{USER_NAME}}</span> <i class="far fa-comment"></i> {{COMMENT_DATETIME}}</li>\n' +
                '                                            </ul>\n' +
                '                                        </td>\n' +
                '                                    </tr>\n' +
                '                                </table>\n' +
                '                            </li>';
            this.reply_template = '         <li id="reply{{REPLY_ID}}" class="post-comment">\n' +
                '                                        <table>\n' +
                '                                            <tr>\n' +
                '                                                <td class="comment-user col-md-1">\n' +
                '                                                    <img src="{{USER_IMAGE}}" alt="" class="comment-avatar">\n' +
                '                                                </td>\n' +
                '                                                <td class="post-comment-body col-md-11">\n' +
                '                                                    {{COMMENT}}\n' +
                '                                                    <ul class="post-comment-meta">\n' +
                '                                                        <li><span class="far fa-thumbs-up reply-like{{REPLY_ID}}"> 赞({{COMMENT_N_LIKE}})</span></li>\n' +
                '                                                        <li>|</li>\n' +
                '                                                        <li><span class="reply{{REPLY_ID}}">回复</span></li>\n' +
                '                                                        <li><span class="reply-remove{{REPLY_ID}}">删除</span></li>\n' +
                '                                                        <li class="post-comment-date pull-left"><span class="reply-name{{REPLY_ID}}">{{USER_NAME}}</span> <i class="fas fa-at">{{REPLY_NAME}} </i> <i class="far fa-comment"></i> {{COMMENT_DATETIME}}</li>\n' +
                '                                                    </ul>\n' +
                '                                                </td>\n' +
                '                                            </tr>\n' +
                '                                        </table>\n' +
                '                                    </li>';
            this.reply_root_template = '<ul id="comment-reply{{COMMENT_ID}}" class="comment-comment-list"></ul>';
            this.comment_reply_url = settings.comment_reply_url;
            this.like_dislike_url = settings.like_dislike_url;
            this.ct = $('#content_type').val();
            this.cmt_ct = $('#comment_content_type').val();
            this.object_id = $('#object_id').val();
            this.is_replying = false;
            this.liking_dict = {};
            this.replying_list = [];

            this.load_comment_reply();
        },
        create_comment: function (self) {
            //点击评论创建博文评论
            if (self == null) {
                self = this;
            }

            if (!self.get_cmt_post_data()) {
                return;
            }

            $.post(self.comment_reply_url, self.get_cmt_post_data(), function (data, textStatus, jqXHR) {
                if ($('.post-comment-list').length <= 0) {
                    $('.comment-panel-body').append('<ul class="post-comment-list"></ul>');
                }

                $('.post-comment-list').append(self.render_comment_template(data, self.comment_template));

                //绑定点击事件
                self.bind_cmt_events(data.id);

                //如果是第一条对博文的评论，则需要给评论面板创建一个美观的虚线
                if ($('.comment-panel-body:has(.line)').length <= 0) {
                    $('.comment-panel-body').append('<div class="line"></div>');
                }
            });
        },
        create_reply: function (parent_id, self, type, reply_name) {
            //点击回复创建评论的评论
            if (self == null) {
                self = this;
            }

            if (!self.get_reply_post_data(parent_id)) {
                return;
            }

            $.post(self.comment_reply_url, self.get_reply_post_data(parent_id), function (data, textStatus, jqXHR) {
                if ($('#comment-reply' + parent_id).length <= 0) {
                    $('#' + type + parent_id).append(self.render_reply_root_template({id: parent_id}, self.reply_root_template));
                }

                $('#comment-reply' + parent_id).append(self.render_reply_template(data, self.reply_template, reply_name));

                self.bind_reply_events(data.id);
            });
        },
        load_comment_reply: function () {
            //页面加载创建博文评论以及各个评论的评论
            var self = this;
            $.getJSON(this.comment_reply_url, function (data) {
                if (data.length <= 0) {
                    return;
                }

                $('.comment-panel-body').append('<ul class="post-comment-list"></ul>');

                $.each(data, function (index, comment) {
                    self.build_comment(comment, self.comment_template);
                });

                $('.comment-panel-body .post-comment-list').after('<div class="line"></div>');
            });
        },
        remove_comment: function (cmt_id) {
            //删除博文评论或者回复
        },
        remove_reply: function (reply_id) {

        },
        incr_comment_like: function (reply_id) {
            //博文评论，或者回复，喜欢增加或者减少。
        },
        incr_reply_like: function (reply_id) {

        },
        set_comment_caution: function (label) {
            var username = $('#username').val();
            $('.comment-caution').text(label + ' 当前登陆用户：' + username);
        },
        reset_comment_caution: function () {
            var username = $('#username').val();
            $('.comment-caution').text(' 文明留言， 说说你的看法。 当前登陆用户：' + username);
        },
        get_cmt_content: function () {
            var rich_comment = this.$textarea.val();
            if (rich_comment.trim() == '') {
                this.set_comment_caution('内容不能为空。');
                return false;
            }

            return rich_comment;
        },
        get_cmt_post_data: function () {
            var self = this;

            if (!self.get_cmt_content()) {
                return;
            }

            return {
                content: self.get_cmt_content(),
                content_type: self.ct,
                object_id: self.object_id,
                parent: null,
                author: $('#username').val(),
            }
        },
        get_reply_post_data: function (parent_id) {
            var self = this;

            if (!self.get_cmt_content()) {
                return;
            }

            return {
                content: self.get_cmt_content(),
                content_type: self.cmt_ct,
                object_id: parent_id,
                parent: parent_id,
                author: $('#username').val(),
            };
        },
        render_comment_template: function (data, template) {
            var user_name = data.author.username;
            var user_image = 'images/avatar.png';
            var comment_datetime = data.published_time;
            var comment_content = data.content;
            var comment_n_like = data.n_like;
            var comment_id = data.id;

            var comment_template = template.replace('{{USER_NAME}}', user_name);
            comment_template = comment_template.replace('{{USER_IMAGE}}', user_image);
            comment_template = comment_template.replace('{{COMMENT_DATETIME}}', comment_datetime);
            comment_template = comment_template.replace('{{COMMENT}}', comment_content);
            comment_template = comment_template.replace('{{COMMENT_N_LIKE}}', comment_n_like);
            comment_template = comment_template.replace(/{{COMMENT_ID}}/g, comment_id);

            return comment_template;
        },
        render_reply_root_template: function (data, template) {
            return template.replace('{{COMMENT_ID}}', data.id);
        },
        render_reply_template: function (data, template, reply_name) {
            var user_name = data.author.username;
            var user_image = 'images/avatar.png';
            var comment_datetime = data.published_time;
            var comment_content = data.content;
            var comment_n_like = data.n_like;
            var reply_id = data.id;

            var reply_template = template.replace('{{USER_NAME}}', user_name);
            reply_template = reply_template.replace('{{USER_IMAGE}}', user_image);
            reply_template = reply_template.replace('{{COMMENT_DATETIME}}', comment_datetime);
            reply_template = reply_template.replace('{{COMMENT}}', comment_content);
            reply_template = reply_template.replace('{{COMMENT_N_LIKE}}', comment_n_like);
            reply_template = reply_template.replace('{{REPLY_NAME}}', reply_name);
            reply_template = reply_template.replace(/{{REPLY_ID}}/g, reply_id);

            return reply_template;
        },
        build_comment: function (data, template) {
            var self = this;

            $('.post-comment-list').append(self.render_comment_template(data, template));

            //绑定 删除 回复 点赞的 点击事件回调
            self.bind_cmt_events(data.id);

            if (data.children.length > 0) {
                $('#comment' + data.id).append(self.render_reply_root_template(data, self.reply_root_template));

                $.each(data.children, function (index, reply) {
                    self.build_reply(reply, self.reply_template, data.author.username);
                });
            }
        },
        build_reply: function (data, template, reply_name) {
            var self = this;

            $('#comment-reply' + data.parent).append(self.render_reply_template(data, template, reply_name));
            //绑定 删除 回复 点赞的 点击事件回调
            self.bind_reply_events(data.id);

            if (data.children.length > 0) {
                $('#reply' + data.id).append(self.render_reply_root_template(data, self.reply_root_template));

                $.each(data.children, function (index, reply) {
                    self.build_reply(reply, self.reply_template, data.author.username);
                });
            }
        },
        bind_cmt_events: function (cmt_id) {
            var self = this;
            //回复
            $('#comment' + cmt_id).on('click', '.comment' + cmt_id, function () {
                self.reset_comment_caution();

                if (!self.is_replying) {
                    var reply_name = $('.comment-name' + cmt_id).text();
                    var label = '@ ' + reply_name;
                    $('.comment-btn').text(label);
                    self.$textarea[0].focus();

                    self.reset_comment_btn_click(self.create_reply, cmt_id, 'comment', reply_name);
                    $('.comment' + cmt_id).text('取消回复');
                    self.replying_list.push('.comment' + cmt_id);
                    self.is_replying = true;
                }
                else {
                    self.reset_comment_btn_click();
                    self.is_replying = false;
                    $(self.replying_list.pop()).text('回复');
                    $('.comment-btn').text('发表');
                }
            });
            //删除
            $('#comment' + cmt_id).on('click', '.comment-remove' + cmt_id, function () {
                var del_url = self.comment_reply_url + cmt_id + '/';
                $.ajax({
                    url: del_url,
                    type: 'DELETE',
                    success: function () {
                        $('#comment' + cmt_id).remove();
                        //顺便把评论面板下的虚线也删除了
                        if ($('.post-comment-list:has(.post-comment)').length <= 0) {
                            $('.comment-panel-body .line').remove();
                        }
                    }
                });
            });
            //点赞
            $('#comment' + cmt_id).on('click', '.comment-like' + cmt_id, function () {
                var like_url = self.comment_reply_url + cmt_id + '/' + 'like' + '/';
                var dislike_url = self.comment_reply_url + cmt_id + '/' + 'dislike' + '/';

                if (self.liking_dict['.comment-like' + cmt_id] != '.comment-like' + cmt_id) {
                    $.ajax({
                        url: like_url,
                        type: 'POST',
                        success: function (data) {
                            $('.comment-like' + cmt_id).text('赞(' + data.n_like + ')');
                        }
                    });

                    self.liking_dict['.comment-like' + cmt_id] = '.comment-like' + cmt_id;
                    $('.comment-like' + cmt_id).removeClass('far');
                    $('.comment-like' + cmt_id).addClass('fas');
                }
                else {
                    $.ajax({
                        url: dislike_url,
                        type: 'POST',
                        success: function (data) {
                            $('.comment-like' + cmt_id).text('赞(' + data.n_like + ')');
                        }
                    });

                    delete self.liking_dict['.comment-like' + cmt_id];
                    $('.comment-like' + cmt_id).removeClass('fas');
                    $('.comment-like' + cmt_id).addClass('far');
                }
            });
        },
        bind_reply_events: function (reply_id) {
            var self = this;
            //回复
            $('#reply' + reply_id).on('click', '.reply' + reply_id, function () {
                //点击回复的时候，让textarea获得焦点。最后通过.comment-btn完成回复
                self.reset_comment_caution();

                if (!self.is_replying) {
                    var reply_name = $('.reply-name' + reply_id).text();
                    var label = '@ ' + reply_name;
                    $('.comment-btn').text(label);
                    self.$textarea[0].focus();
                    //重新绑定comment-btn点击事件.
                    self.reset_comment_btn_click(self.create_reply, reply_id, 'reply', reply_name);
                    $('.reply' + reply_id).text('取消回复');
                    self.replying_list.push('.reply' + reply_id);
                    self.is_replying = true;
                }
                else {
                    self.reset_comment_btn_click();
                    self.is_replying = false;
                    $(self.replying_list.pop()).text('回复');
                    $('.comment-btn').text('发表');
                }
            });
            //删除
            $('#reply' + reply_id).on('click', '.reply-remove' + reply_id, function () {
                var del_url = self.comment_reply_url + reply_id + '/';
                $.ajax({
                    url: del_url,
                    type: 'DELETE',
                    success: function () {
                        $('#reply' + reply_id).remove();
                        //顺便把评论面板下的虚线也删除了
                        if ($('.post-comment-list:has(.post-comment)').length <= 0) {
                            $('.comment-panel-body .line').remove();
                        }
                    }
                });
            });
            //点赞
            $('#reply' + reply_id).on('click', '.reply-like' + reply_id, function () {
                var like_url = self.comment_reply_url + reply_id + '/' + 'like' + '/';
                var dislike_url = self.comment_reply_url + reply_id + '/' + 'dislike' + '/';

                if (self.liking_dict['.reply-like' + reply_id] != '.reply-like' + reply_id) {
                    $.ajax({
                        url: like_url,
                        type: 'POST',
                        success: function (data) {
                            $('.reply-like' + reply_id).text('赞(' + data.n_like + ')');
                        }
                    });

                    self.liking_dict['.reply-like' + reply_id] = '.reply-like' + reply_id;
                    $('.reply-like' + reply_id).removeClass('far');
                    $('.reply-like' + reply_id).addClass('fas');
                }
                else {
                    $.ajax({
                        url: dislike_url,
                        type: 'POST',
                        success: function (data) {
                            $('.reply-like' + reply_id).text('赞(' + data.n_like + ')');
                        }
                    });

                    delete self.liking_dict['.reply-like' + reply_id];
                    $('.reply-like' + reply_id).removeClass('fas');
                    $('.reply-like' + reply_id).addClass('far');
                }
            });
        },
        reset_comment_btn_click: function (f, pid, type, reply_name) {
            var self = this;

            if (!self.is_replying) {
                $('.comment-panel-header-body').off('click', '.comment-btn');
                $('.comment-panel-header-body').on('click', '.comment-btn', function () {
                    f(pid, self, type, reply_name);
                });
            }
            else {
                $('.comment-panel-header-body').off('click', '.comment-btn');
                $('.comment-panel-header-body').on('click', '.comment-btn', function () {
                    self.create_comment(self);
                });
            }
        }
    };

    window.MyBlogComment = MyBlogComment;
});
