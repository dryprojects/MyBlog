#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      views.py 
@time:      2018/07/29 
""" 

from blog import models
from blog.api import serializers

from rest_framework import viewsets
from rest_framework import filters as rest_filters
from django_filters import rest_framework as filters

from blog.api import paginators
from blog.api import filters as blog_filters
from blog.api import permissions


class PostReadOnlyViewset(viewsets.ReadOnlyModelViewSet):
    """
    # 只读博文接口, 不可删除，增加/更新博文
    """
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostListSerializer
    pagination_class = paginators.PostPaginator
    filter_backends = (filters.DjangoFilterBackend, rest_filters.SearchFilter, rest_filters.OrderingFilter,) #rest_filters.DjangoObjectPermissionsFilter
    filter_class = blog_filters.PostFilter  # 注意这里不是重写 filterset_class 属性
    search_fields = ('title', 'category__name')
    ordering_fields = ('published_time', 'n_praise', 'n_browsers')
    ordering = ('-published_time', ) #默认排序规则
    permission_classes = (permissions.IsOwnerOrReadOnly,)


class PostViewset(viewsets.ModelViewSet):
    """
    博文读写接口
    """
    queryset = models.Post.objects.all()
    pagination_class = paginators.PostPaginator
    filter_backends = (filters.DjangoFilterBackend, rest_filters.SearchFilter, rest_filters.OrderingFilter)
    filter_class = blog_filters.PostFilter  # 注意这里不是重写 filterset_class 属性
    search_fields = ('title', 'category__name')
    ordering_fields = ('published_time', 'n_praise', 'n_browsers')
    ordering = ('-published_time', ) #默认排序规则

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            permission_classes = [permissions.IsOwnerOrReadOnly]
        else:
            # 需要客户不在黑名单，且具有对应博文实例的读取权限
            permission_classes = [permissions.BlacklistPermission, permissions.ReadPermission]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return serializers.PostDetailSerializer
        else:
            return serializers.PostListSerializer


class CategoryViewset(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategoryTreeSerializer


class TagViewset(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class ResourceViewset(viewsets.ModelViewSet):
    queryset = models.Resources.objects.all()
    serializer_class = serializers.ResourceSerializer