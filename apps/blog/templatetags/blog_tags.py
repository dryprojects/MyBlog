# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/27 19:06'

from django import template

from blog.models import Post
from blog import enums


register = template.Library()

@register.simple_tag
def get_post_archive_count(year, month):
    return Post.objects.filter(published_time__year=year, published_time__month=month, post_type=enums.POST_TYPE_POST).count()