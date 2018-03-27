# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/27 13:32'

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
