# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/23 17:28'


from django.db.models import ObjectDoesNotExist
from django.core.cache import cache
from django.contrib.auth import get_user_model
from blog.tasks import task_lock


from celery import shared_task
from celery.utils.log import get_task_logger

from oper.models import NotificationUnReadCounter


logger = get_task_logger(__name__)
User = get_user_model()
key_tmpplate = "oper:notification:%s"


@shared_task(bind=True)
def update_n_unread(self, user_id, value):
    """
    更新用户未读数量
        1. 若缓存中存在用户的未读数，更新缓存。
        2. 若缓存中不存在， 则在缓存中新建用户的未读计数器。
    :param self:
    :param user_id:
    :param value:
    :return:
    """
    key = key_tmpplate%user_id

    if not cache.has_key(key):
        user = User.objects.get(pk=user_id)
        nc_obj = NotificationUnReadCounter(user=user)

        cache.set(key, nc_obj.n_unread, None)
        logger.debug("set in cache %s, %s"%(key, nc_obj.n_unread))

    ret = cache.incr(key, value)
    logger.debug("incr in cache %s, %s" % (key, ret))


@shared_task(bind=True)
def get_n_unread(self, user_id):
    """
    获取用户未读消息数量
        1. 若缓存中存在，直接返回。
        2. 若缓存中不存在，首先从数据库中读取到缓存。
    :param self:
    :param user_id:
    :return:
    """
    key = key_tmpplate % user_id

    if not cache.has_key(key):
        # try:
        #     nc_obj = NotificationUnReadCounter.objects.get(pk=user_id)
        # except ObjectDoesNotExist:
        #     user = User.objects.get(pk=user_id)
        #     nc_obj = NotificationUnReadCounter.objects.create(user=user)
        #
        # cache.set(key, nc_obj.n_unread, None)
        return None
    return cache.get(key)


@shared_task(bind=True)
def sync_n_unread(self):
    """
    定时任务
    1. 将缓存中的未读数同步到数据库
    2. 将缓存中对应的键删除
    :param self:
    :return:
    """
    lock_key = key_tmpplate%("mutex_lock")

    with task_lock(lock_key, self.app.oid) as aquired:
        if aquired:
            for noti_keys in filter(lambda x: x.startswith('oper:notification:'), cache.keys('*')):
                if noti_keys is not None:
                    try:
                        user_id = noti_keys.split(':').pop()
                        user = User.objects.get(pk=user_id)
                        user_n_unread = get_n_unread.delay(user_id)

                        noti_counter = NotificationUnReadCounter.objects.get(user=user)
                        noti_counter.n_unread = user_n_unread.get()
                        noti_counter.save()
                    except Exception as e:
                        logger.debug(repr(e))
                        return
                    else:
                        cache.delete(noti_keys)
                        return
                else:
                    return
    logger.debug('sync_n_unread is already being worked by another worker')