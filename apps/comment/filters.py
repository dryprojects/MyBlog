#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      filter.py 
@time:      2018/08/04 
"""

from comment.models import Comment

from django_filters import rest_framework as filters


class CommentFilter(filters.FilterSet):
    class Meta:
        model = Comment
        fields = {
            'parent': ['exact', "isnull"],
            "content_type": ['exact'],
            "object_id": ['exact']
        }
