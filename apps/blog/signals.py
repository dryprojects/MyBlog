# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/27 13:32'

from django.db.models.signals import post_save, post_delete
from django.core.signals import request_finished
from django.dispatch import receiver, Signal
from blog.models import Post
from django.conf import settings

@receiver(post_save, sender=Post)
def inform(sender, **kwargs):
    print("complete save!")
    print(sender)
    print(kwargs)