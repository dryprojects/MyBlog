# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/23 17:28'


from django.db.models import ObjectDoesNotExist
from django.core.cache import cache
from django.contrib.auth import get_user_model

from celery import shared_task
from celery.utils.log import get_task_logger

from oper.models import NotificationUnReadCounter


logger = get_task_logger(__name__)
User = get_user_model()
key_tmpplate = "oper:notification:%s"


@shared_task(bind=True)
def update_n_unread(self, user_id, value):
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
    key = key_tmpplate % user_id

    if not cache.has_key(key):
        try:
            nc_obj = NotificationUnReadCounter.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            user = User.objects.get(pk=user_id)
            nc_obj = NotificationUnReadCounter.objects.create(user=user)

        cache.set(key, nc_obj.n_unread, None)
    return cache.get(key)