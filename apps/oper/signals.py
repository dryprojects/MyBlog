# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/23 13:54'


from django.dispatch import receiver, Signal
from django.db.models.signals import post_save, post_delete

from oper.models import Notification, NotificationUnReadCounter
from oper.tasks import update_n_unread


@receiver(post_save, sender=Notification)
def incr_n_unread(sender, instance, created, **kwargs):
    if not created or instance.has_read:
        return
    #开始计数
    if not any(NotificationUnReadCounter.objects.filter(user=instance.user)):
        NotificationUnReadCounter.objects.create(user=instance.user)
    update_n_unread.delay(instance.user.id, 1)


@receiver(post_delete, sender=Notification)
def decr_n_unread(sender, instance, **kwargs):
    if not instance.has_read:
        update_n_unread.delay(instance.user.id, -1)