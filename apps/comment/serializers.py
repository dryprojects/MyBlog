# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/22 11:12'


from django.contrib.auth import get_user_model

from rest_framework import serializers

from drf_writable_nested import WritableNestedModelSerializer

from comment.models import Comment


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class CommentTreeSerializer(WritableNestedModelSerializer):
    children = serializers.SerializerMethodField()
    author = UserSerializer()

    class Meta:
        model = Comment
        fields = ['parent', 'id', 'content', 'author', 'content_type', 'object_id',
                  'published_time', 'n_like', 'n_dislike', 'is_spam', 'children']

    def get_children(self, parent):
        queryset = parent.get_children()
        serialized_data = CommentTreeSerializer(queryset, many=True, read_only=True, context=self.context)
        return serialized_data.data