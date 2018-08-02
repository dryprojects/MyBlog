#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      serializers.py 
@time:      2018/05/03 
"""

from rest_framework import serializers
from drf_writable_nested import NestedCreateMixin, NestedUpdateMixin

from blog.models import Category, Post, Tag, Resources


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, parent):
        queryset = parent.get_children()
        serializer = CategoryTreeSerializer(queryset, many=True, read_only=True, context=self.context)

        return serializer.data

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'children']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class BasePostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        extra_kwargs = {
            'url': {'view_name': "blog:post-detail"},
            'parent': {'view_name': "blog:post-detail"},
            'children': {'view_name': "blog:post-detail"},
            'category': {'view_name': "blog:category-detail"},
            'tags': {'view_name': "blog:tag-detail"},
            'author': {'view_name': 'bloguser:user-detail'}
        }


class PostListSerializer(BasePostSerializer):
    class Meta(BasePostSerializer.Meta):
        fields = (
            'url',
            'title',
            'excerpt',
            'cover',
            'n_praise',
            'n_comments',
            'n_browsers',
            'published_time'
        )


class PostSerializer(NestedCreateMixin, NestedUpdateMixin, BasePostSerializer):

    class Meta(BasePostSerializer.Meta):
        fields = (
            'url',
            'title',
            'category',
            'tags',
            'author',
            'content',
            'cover',
            'status',
            'post_type',
            'is_free',
            'parent'
        )


class PostDetailSerializer(BasePostSerializer):
    tags = TagSerializer(many=True)
    category = CategorySerializer()
    children = serializers.SerializerMethodField()

    def get_children(self, parent):
        queryset = parent.get_children()
        serializer = PostListSerializer(queryset, many=True, read_only=True, context=self.context)
        return serializer.data

    class Meta(BasePostSerializer.Meta):
        exclude = (
            'lft',
            'rght',
            'tree_id',
            'level',
            'cover_url'
        )


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = "__all__"
