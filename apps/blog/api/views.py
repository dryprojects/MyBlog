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
from rest_framework.response import Response
from rest_framework import filters as rest_filters
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from dry_rest_permissions.generics import DRYPermissions

from blog.api import paginators
from blog.api import filters as blog_filters
from blog.api import permissions


class PostViewset(viewsets.ModelViewSet):
    """
    博文读写接口
    """
    queryset = models.Post.objects.all()
    pagination_class = paginators.PostPaginator
    permission_classes = (permissions.BlacklistPermission, DRYPermissions)
    filter_backends = (filters.DjangoFilterBackend, blog_filters.PostFilterBackend, rest_filters.OrderingFilter, rest_filters.SearchFilter)
    filter_class = blog_filters.PostFilter  # 注意这里不是重写 filterset_class 属性
    search_fields = ('title', 'category__name')
    ordering_fields = ('published_time', 'n_praise', 'n_browsers')
    ordering = ('-published_time', ) #默认排序规则

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
        返回属于公告的博文
        :return:
        """
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True, context={'request':self.request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': self.request})
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