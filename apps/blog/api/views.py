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


class PostReadOnlyViewset(viewsets.ReadOnlyModelViewSet):
    """
    只读博文接口, 不可删除，增加/更新博文
    """
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostLinkedSerializer


class PostViewset(viewsets.ModelViewSet):
    """
    博文读写接口
    """
    queryset = models.Post.objects.all()
    serializer_class = serializers.PostLinkedSerializer


class CategoryViewset(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategoryTreeSerializer


class TagViewset(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class ResourceViewset(viewsets.ModelViewSet):
    queryset = models.Resources.objects.all()
    serializer_class = serializers.ResourceSerializer