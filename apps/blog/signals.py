# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/27 13:32'

from django.db.models.signals import pre_save
from django.dispatch import receiver, Signal
from blog.models import Post


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