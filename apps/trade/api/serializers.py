#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      serializers.py 
@time:      2018/08/16 
"""

from rest_framework import serializers

from generic_relations.relations import GenericRelatedField, GenericSerializerMixin

from trade import models
from blog import models as blog_models
from blog.api import serializers as blog_serializers


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    content_object = GenericRelatedField({
        blog_models.Post: blog_serializers.PostListSerializer()
    })

    class Meta:
        model = models.ShoppingCart
        fields = ('user', 'content_object', 'n_goods', 'created_time')