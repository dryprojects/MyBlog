#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      views.py 
@time:      2018/07/29 
"""

from rest_framework import viewsets, filters as rest_filters, throttling as rest_throttling
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters import rest_framework as filters

from blog import models, enums
from blog.api import serializers, paginators, permissions, throttling, filters as blog_filters


class PostViewset(viewsets.ModelViewSet):
    """
    ### list:
        返回用户所有公开发表的博文，当前用户返回所有的博文
    ### retrieve:
        返回的博文如果是私有的则需要对应权限才可访问
    """
    queryset = models.Post.objects.all()
    pagination_class = paginators.PostPaginator
    permission_classes = (permissions.BlacklistPermission, permissions.DRYPostPermissions)
    throttle_classes = (throttling.PostUserRateThrottle, rest_throttling.AnonRateThrottle)
    filter_backends = (filters.DjangoFilterBackend, rest_filters.OrderingFilter, rest_filters.SearchFilter, blog_filters.PostFilterBackend)
    filter_class = blog_filters.PostFilter  # 注意这里不是重写 filterset_class 属性
    search_fields = ('title', 'category__name')
    ordering_fields = ('published_time', 'n_praise', 'n_browsers')
    ordering = ('-published_time',)  # 默认排序规则

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return serializers.PostDetailSerializer
        elif self.action in ["update", "partial_update", "create"]:
            return serializers.PostSerializer
        else:
            return serializers.PostListSerializer

    @action(detail=False)
    def notifications(self, request):
        """
        ### list: 返回站点公告
        """
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True, context={'request': self.request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': self.request})
        return Response(serializer.data)

    @action(detail=False)
    def archives(self, request):
        """### list: 返回博文按照月份的归档"""
        queryset = self.get_queryset()
        query = {
            'status': enums.POST_STATUS_PUBLIC,
            'post_type': enums.POST_TYPE_POST
        }
        queryset = queryset.filter(**query)
        date_queryset= self.filter_queryset(queryset)

        page = self.paginate_queryset(date_queryset)
        if page:
            serializer = serializers.PostArchiveSerializer(page, many=True, context={'request': self.request, 'queryset':queryset})
            return self.get_paginated_response(serializer.data)
        serializer = serializers.PostArchiveSerializer(date_queryset, many=True, context={'request': self.request, 'queryset':queryset})
        return Response(serializer.data)


class CategoryViewset(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategoryTreeSerializer


class TagViewset(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class ResourceViewset(viewsets.ModelViewSet):
    queryset = models.Resources.objects.all()
    serializer_class = serializers.ResourceSerializer
