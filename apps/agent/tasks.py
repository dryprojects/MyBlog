#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      tasks.py 
@time:      2018/06/23 
""" 

import os

from celery import shared_task
from celery.utils.log import get_task_logger

from contextlib import contextmanager
from django.core.cache import cache
from celery.five import monotonic

logger = get_task_logger(__name__)
LOCK_EXPIRE = 60 * 1


@contextmanager
def task_lock(lock_id, oid):
    """
    用缓存实现对任务加锁:
        One issue we have is that for several of our periodic tasks,
        we need to ensure that only one task is running at a time,
        and that later instances of the same periodic task are skipped
        if a previous incarnation is still running.
        防止同一个任务在同一时间被多个worker所操作。
        用于保证同一个定时任务同一时间只被一个worker在执行。
    用法:
        with task_lock(lock_id:key, self.app.oid:value) as acquired:
        if acquired: 如果没有竞争者
            do_something()
    see more:
        http://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html#cookbook-task-serial
        http://loose-bits.com/2010/10/distributed-task-locking-in-celery.html
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
def post_crawler(self):
    """
    定时抓取博文
    :param self:
    :return:
    """
    from agent.robot.robot.spiders.jobbole import JobboleSpider
    from agent.robot.robot.run import CrawlerScript

    os.environ['SCRAPY_SETTINGS_MODULE'] = 'agent.robot.robot.settings'

    lock_key = __name__ + ".mutex_lock"
    with task_lock(lock_key, self.app.oid) as aquired:
        if aquired:
            CrawlerScript([JobboleSpider]).start()
        else:
            logger.info("另一个crawler正在运行。")