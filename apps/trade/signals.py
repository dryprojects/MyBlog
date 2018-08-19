#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      signals.py 
@time:      2018/08/02 
""" 

import time
import datetime
import random

from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver, Signal

from trade import models


def gen_order_sn(goods_order):
    """生成订单号"""
    def random_order_sn():
        """随即订单号"""
        return "{time}{user_id}{random_str}".format(
            time=time.strftime("%Y%m%d%H%M%S"),
            user_id=goods_order.user.id,
            random_str=random.Random().randint(10, 99))

    goods_order.order_sn = random_order_sn()

@receiver(pre_save, sender=models.GoodsOrder)
def on_goods_order_prev_save(sender, **kwargs):
    goods_order = kwargs['instance']

    gen_order_sn(goods_order)