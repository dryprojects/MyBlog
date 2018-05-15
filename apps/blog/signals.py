# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/27 13:32'

from django.db.models.signals import pre_save
from django.dispatch import receiver, Signal
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.utils.html import mark_safe, format_html
from django.template import loader

from blog.models import Post
from comment.models import Comment
from comment.signals import post_comment, post_like


@receiver(pre_save, sender=Post)
def gen_excerpt(sender, instance, **kwargs):
    """
    在保存前如果博文摘要为空， 则自动生成摘要
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """

    if instance.excerpt is '':
        instance.excerpt = instance.content[:400]


@receiver(post_comment, sender=Comment)
def handler_post_comment(sender, comment_obj, content_type, object_id, request, **kwargs):
    post_ct = ContentType.objects.get_for_model(Post)
    comment_ct = ContentType.objects.get_for_model(Comment)
    email_post_comment_template = 'blog/email/email_post_comment.html'
    email_comment_reply_template = 'blog/email/email_comment_reply.html'

    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'

    if content_type == post_ct:
        """博文评论"""
        try:
            post = Post.objects.get(pk=object_id)
        except Post.DoesNotExist as e:
            pass
        else:
            context = {
                'post': post,
                'site_name': site_name,
                'comment_object': comment_obj,
                'protocol': protocol,
                'domain': domain
            }
            # 给博文作者发送一条消息和一份邮件
            subject = '{} 博文 {} {}://{}{} 收到 {} 的评论'.format(site_name, post.title, protocol, domain,
                                                            post.get_absolute_url(), comment_obj.author)
            noti_text = '{} 博文 {} {}://{}{} 收到 {} 的评论 {}'.format(site_name, post.title, protocol, domain,
                                                               post.get_absolute_url(), comment_obj.author,
                                                               mark_safe(comment_obj.content))
            message = loader.render_to_string(email_post_comment_template, context)
            post.author.notify_user(noti_text)
            post.author.email_user(subject, message, html_msg=message)
