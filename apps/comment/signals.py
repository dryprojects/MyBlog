# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/22 12:32'


from django.dispatch import receiver, Signal
from comment.models import Comment


post_like = Signal(providing_args=['comment_obj', 'content_type', 'object_id', 'request'])
post_comment = Signal(providing_args=['comment_obj', 'content_type', 'object_id', 'request'])


# @receiver(post_like, sender=Comment)
# def handler_post_like(sender, comment_obj, content_type, object_id, **kwargs):
#     print("post_like sender:%s, comment:%s, content_type:%s, object_id:%s"%(sender, comment_obj, content_type, object_id))
#
#