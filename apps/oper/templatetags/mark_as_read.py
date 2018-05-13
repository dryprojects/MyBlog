#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      mark_as_read.py 
@time:      2018/05/13 
""" 

from django import template

from oper.tasks import mark_as_read


register = template.Library()


@register.filter(name='mark_as_read')
def mark_user_noti_as_read(noti):
    # 更新缓存
    mark_as_read(noti.user.pk, noti.pk)

    return noti