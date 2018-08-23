#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      serializers.py 
@time:      2018/08/24 
""" 

from rest_framework import serializers

from generic_relations.relations import GenericRelatedField

from blog.api.serializers import PostListSerializer
from blog.models import Post
from oper.models import UserFavorite


class UserFavoriteSerializer(serializers.ModelSerializer):
    content_object = GenericRelatedField({
        Post: PostListSerializer()
    })

    class Meta:
        model = UserFavorite
        fields = ('content_object', 'add_time')
