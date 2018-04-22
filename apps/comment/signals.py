# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/22 12:32'


from django.dispatch import receiver, Signal


post_like = Signal(providing_args=['comment_obj'])
post_dislike = Signal(providing_args=['comment_obj'])