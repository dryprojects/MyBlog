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

    // Comment
    function MyBlogComment(settings) {
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
                '                                                <li><span class="far fa-thumbs-up comment-like"> 赞({{COMMENT_N_LIKE}})</span></li>\n' +
                '                                                <li>|</li>\n' +
                '                                                <li><span class="comment-reply">回复</span></li>\n' +
                '                                                <li><span class="comment-remove">删除</span></li>\n' +
                '                                                <li class="post-comment-date pull-left">{{USER_NAME}} <i class="far fa-comment"></i> {{COMMENT_DATETIME}}</li>\n' +
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
                '                                                        <li><span class="far fa-thumbs-up comment-like"> 赞({{COMMENT_N_LIKE}})</span></li>\n' +
                '                                                        <li>|</li>\n' +
                '                                                        <li><span class="comment-reply">回复</span></li>\n' +
                '                                                        <li><span class="comment-remove">删除</span></li>\n' +
                '                                                        <li class="post-comment-date pull-left">{{USER_NAME}} <i class="fas fa-at"> {{REPLY_NAME}} </i> <i class="far fa-comment"></i> {{COMMENT_DATETIME}}</li>\n' +
                '                                                    </ul>\n' +
                '                                                </td>\n' +
                '                                            </tr>\n' +
                '                                        </table>\n' +
                '                                    </li>';
            this.comment_reply_url = settings.comment_reply_url;
            this.like_dislike_url = settings.like_dislike_url;
            this.ct = window.location.pathname.split('/')[1];
            this.object_id = window.location.pathname.split('/')[1];
            
            this.load_post_comment_reply();
        },
        create_post_comment: function () {
            //点击评论创建博文评论
            var self = this;
            var rich_comment = this.$textarea.val()
            if (rich_comment.trim() == ''){
                return ;
            }
            // 获取博文的ct类型。
            //获取博文的id。

            var jqXHR =  $.post(self.comment_reply_url, {content:rich_comment}, function (data, textStatus, jqXHR) {

            });
            jqXHR.error(function() { alert("error"); });
        },
        create_comment_reply: function () {
            //点击回复创建评论的评论
        },
        load_post_comment_reply: function () {
            //页面加载创建博文评论以及各个评论的评论
            var self = this;
            $.getJSON(this.comment_reply_url, function (data) {
                if (data.length <= 0){
                    return ;
                }

                $('.comment-panel-body').append('<ul class="post-comment-list"></ul>');

                $.each(data, function (index, comment) {
                    self.build_comment(comment, self.comment_template);
                });

                $('.comment-panel-body .post-comment-list').after('<div class="line"></div>');
            });
        },
        remove_comment: function () {
            //删除博文评论或者回复
        },
        incr_like: function () {
            //博文评论，或者回复，喜欢增加或者减少。
        },
        build_comment:function (data, template) {
            var self = this;
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
            comment_template = comment_template.replace('{{COMMENT_ID}}', comment_id);

            $('.post-comment-list').append(comment_template);

            if (data.children.length > 0){
                var reply_name = user_name;
                var reply_root_template = '<ul id="comment-reply{{COMMENT_ID}}" class="comment-comment-list"></ul>';
                reply_root_template =  reply_root_template.replace('{{COMMENT_ID}}', comment_id);

                $('#comment'+comment_id).append(reply_root_template);

                $.each(data.children, function (index, reply) {
                    self.build_reply(reply, self.reply_template, reply_name);
                });
            }
        },
        build_reply:function (data, template, reply_name) {
            var self = this;
            var user_name = data.author.username;
            var user_image = 'images/avatar.png';
            var comment_datetime = data.published_time;
            var comment_content = data.content;
            var comment_n_like = data.n_like;
            var reply_id = data.id;
            var reply_parent_id = data.parent;

            var reply_template = template.replace('{{USER_NAME}}', user_name);
            reply_template = reply_template.replace('{{USER_IMAGE}}', user_image);
            reply_template = reply_template.replace('{{COMMENT_DATETIME}}', comment_datetime);
            reply_template = reply_template.replace('{{COMMENT}}', comment_content);
            reply_template = reply_template.replace('{{COMMENT_N_LIKE}}', comment_n_like);
            reply_template = reply_template.replace('{{REPLY_NAME}}', reply_name);
            reply_template = reply_template.replace('{{REPLY_ID}}', reply_id);

            $('#comment-reply'+reply_parent_id).append(reply_template);

            if (data.children.length > 0){
                reply_name = user_name;
                var reply_root_template = '<ul id="comment-reply{{COMMENT_ID}}" class="comment-comment-list"></ul>';
                reply_root_template = reply_root_template.replace('{{COMMENT_ID}}', reply_id);

                $('#reply'+reply_id).append(reply_root_template);

                $.each(data.children, function (index, reply) {
                    console.log(reply);
                    self.build_reply(reply, self.reply_template, reply_name);
                });
            }
        },
    };

    window.MyBlogComment = MyBlogComment;
});
