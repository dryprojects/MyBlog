# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/23 13:54'


from django.dispatch import receiver, Signal
from django.db.models.signals import post_save, post_delete

from oper.models import Notification


@receiver(post_save, sender=Notification)
def incr_n_unread(sender, instance, created, **kwargs):
    if not created or instance.has_read:
        return

    # incr n_unread