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


# def mark_as_read(self, instance, notification_id):
#     """
#
#     :param self:
#     :param instance:
#     :param notification_id:
#     :return:
#     """
#     from oper.models import Notification
#     #写成一条语句，更新has_read，相当于把这些操作看成一次事务，自动加锁。
#     #这样如果并发时有多个请求更改has_read的操作，其它请求会等待在第一个请求执行完has_read=True
#     #最后其它请求就会知道has_read已经为True了。
#     #这里的has_read会被竞争性访问修改，只有保证了这一步的原子性，下一步原子更新未读数才有意义。
#     affected_rows = Notification.objects.filter(pk=notification_id, has_read=False).update(has_read=True)
#     update_n_unread.delay(instance.user.id, -affected_rows)