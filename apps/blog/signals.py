# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/27 13:32'

from django.db.models.signals import pre_save
from django.dispatch import receiver, Signal
from blog.models import Post
from django.conf import settings

@receiver(pre_save, sender=Post)
def gen_excerpt(sender, **kwargs):
    """

    :param sender:
    :param kwargs:
    :return:
    """

