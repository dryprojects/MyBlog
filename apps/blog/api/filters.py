#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      filters.py 
@time:      2018/07/30 
"""

from blog.models import Post, Category
from blog import enums

from django_filters import rest_framework as filters
from dry_rest_permissions.generics import DRYPermissionFiltersBase


class PostFilter(filters.FilterSet):
    class Meta:
        model = Post
        fields = {
            'parent': ['exact'],
            'title': ['icontains'],
            'tags': ['icontains'],
            'category':['exact'],
            'published_time': ['year__exact', 'month__exact']
        }


class PostFilterBackend(DRYPermissionFiltersBase):
    """
    过滤博文列表
    """
    action_routing = True

    def filter_list_queryset(self, request, queryset, view):
        """
        返回所有用户已公开（发表）的博文，返回当前用户所有的博文（匿名用户只可查看公开博文）
        """
        query = {
            'status': enums.POST_STATUS_PUBLIC,
            'post_type': enums.POST_TYPE_POST
        }
        return queryset.filter(**query)

    def filter_notifications_queryset(self, request, queryset, view):
        """
        返回属于公告的博文
        """
        query = {
            'status': enums.POST_STATUS_PUBLIC,
            'post_type': enums.POST_TYPE_NOTIFICATION
        }
        return queryset.filter(**query)

    def filter_archives_queryset(self, request, queryset, view):
        """
        返回博文的归档列表
        """
        queryset = self.filter_list_queryset(request, queryset, view)
        return queryset.dates('published_time', 'month', order='DESC')


class CategoryFilter(filters.FilterSet):
    class Meta:
        model = Category
        fields = {
            'parent': ['isnull', 'exact'],
            'name':['icontains']
        }