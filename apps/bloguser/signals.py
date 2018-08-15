#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      signals.py 
@time:      2018/07/30 
""" 

from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from bloguser.models import UserProfile


def gen_default_avatar(user, created):
    """
    生成用户默认头像
    """
    if created:
        if not user.image_url:
            user.image_url = user.image.url
    return user

@receiver(post_save, sender=UserProfile)
def on_user_post_save(sender, **kwargs):
    user, created = kwargs['instance'], kwargs['created']

    if created:
        user = gen_default_avatar(user, created)
        user.save()

