#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      filters.py 
@time:      2018/07/30 
"""

from blog.models import Post
from blog import enums

from django_filters import rest_framework as filters
from dry_rest_permissions.generics import DRYPermissionFiltersBase


class PostFilter(filters.FilterSet):
    class Meta:
        model = Post
        fields = {
            'parent__title': ['icontains'],
            'title': ['icontains'],
            'tags': ['icontains'],
            'published_time': ['year__lte', 'year__gte', 'month__gte', 'month__lte', 'day__lte', 'day__gte']
        }


class PostFilterBackend(DRYPermissionFiltersBase):
    """
    过滤博文列表
    """
    action_routing = True

    def filter_list_queryset(self, request, queryset, view):
        """
        返回所有用户已公开（发表）的博文，返回当前用户所有的博文（匿名用户只可查看公开博文）
        :param request:
        :param queryset:
        :param view:
        :return:
        """
        query = {
            'status': enums.POST_STATUS_PUBLIC,
            'post_type': enums.POST_TYPE_POST
        }
        return queryset.filter(**query)

    def filter_notifications_queryset(self, request, queryset, view):
        """
        返回属于公告的博文
        :param request:
        :param queryset:
        :param view:
        :return:
        """
        query = {
            'status': enums.POST_STATUS_PUBLIC,
            'post_type': enums.POST_TYPE_NOTIFICATION
        }
        return queryset.filter(**query)