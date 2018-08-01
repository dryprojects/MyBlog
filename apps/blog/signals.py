# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/27 13:32'

from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver, Signal
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.html import mark_safe, format_html
from django.template import loader

from haystack.signals import BaseSignalProcessor
from guardian.shortcuts import assign_perm

from blog.models import Post
from comment.models import Comment
from comment.signals import post_comment, post_like


post_published = Signal(providing_args=['instance'])
User = get_user_model()


class PostSignalProcessor(BaseSignalProcessor):
    """
    Allows for observing when post update status or post deletes fire & automatically updates the
    search engine appropriately.
    当博文状态改变为已发表时，建立对应博文索引。
    """
    def setup(self):
        # Naive (listen to all post change status).
        post_published.connect(self.handle_save)
        post_delete.connect(self.handle_delete)
        # Efficient would be going through all backends & collecting all models
        # being used, then hooking up signals only for those.

    def teardown(self):
        # Naive (listen to all post change status).
        post_published.disconnect(self.handle_save)
        post_delete.disconnect(self.handle_delete)
        # Efficient would be going through all backends & collecting all models
        # being used, then disconnecting signals only for those.


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
        instance.excerpt = instance.content[:223]

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
    elif content_type == comment_ct:
        """评论回复"""
        try:
            pass
        except Comment.DoesNotExist as e:
            pass
        else:
            comment = Comment.objects.get(pk=object_id)
            context = {
                'comment': comment,
                'site_name': site_name,
                'comment_object': comment_obj,
                'protocol': protocol,
                'domain': domain,
            }
            subject = '你的评论收到{}的回复'.format(comment_obj.author)
            noti_text = '你的评论{}收到{}的回复 {}'.format(comment.content, comment_obj.author, comment_obj.content)
            message = loader.render_to_string(email_comment_reply_template, context)

            comment.author.notify_user(noti_text)
            comment.author.email_user(subject, message, html_msg=message)

@receiver(post_save, sender=Post)
def assign_post_view_perm(sender, **kwargs):
    """
    创建或者获取readers组赋予该组对所有博文实例的读取权限
    """
    post, created = kwargs["instance"], kwargs["created"]
    readers, _= Group.objects.get_or_create(name='readers')
    if _:
        assign_perm('blog.view_post', readers) # 给readers组赋予可以访问所有博文实例的模型权限
        assign_perm('blog.add_post', readers)
    if created:
        assign_perm("view_post", readers, post) #给readers组赋予可访问指定的博文的对象权限
        assign_perm('blog.change_post', post.author, post) #给博文作者分配修改和删除博文的模型权限
        assign_perm('blog.delete_post', post.author, post)

@receiver(post_save, sender=User)
def user_as_reader(sender, **kwargs):
    user, created = kwargs['instance'], kwargs['created']

    if created and not user.is_anonymous:
        readers, _ = Group.objects.get_or_create(name='readers')
        if _:
            assign_perm('blog.view_post', readers)
            assign_perm('blog.add_post', readers)
        user.groups.add(readers)