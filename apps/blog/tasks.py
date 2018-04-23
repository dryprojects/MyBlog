from __future__ import absolute_import, unicode_literals
# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/23 15:20'


from contextlib import contextmanager

from django.core.cache import cache

from celery import shared_task
from celery.five import monotonic  #vine.five.monotonic
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)
LOCK_EXPIRE = 60 * 1 # Lock expires in 1 minutes

@contextmanager
def cache_lock(lock_id, oid):
    """
    用缓存实现加锁:
        防止定时任务，重复提交。
        防止多个woker竞争cache。
        防止对cache的竞争性访问。
    用法:
        with cache_lock(lock_id:key, self.app.oid:value) as acquired:
        if acquired: 如果没有竞争者
            do_something()
    see more:
        http://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html#cookbook-task-serial

    :param lock_id:
    :param oid:
    :return:
    """
    timeout_at = monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    #add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None, client=None):
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if monotonic() < timeout_at:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else.
            cache.delete(lock_id)


@shared_task(bind=True)
def sync_redis(self, *args, **kwargs):
    pass