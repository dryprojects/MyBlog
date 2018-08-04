# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/22 11:12'

from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from comment.models import Comment
from comment.signals import post_comment
from bloguser.api.serializers import UserSerializer


class CommentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    author = UserSerializer(required=False, read_only=True)

    class Meta:
        model = Comment
        fields = ['parent', 'id', 'content', 'author', 'content_type', 'object_id',
                  'published_time', 'n_like', 'n_dislike', 'is_spam', 'children']
        read_only_fields = ('n_like', 'n_dislike', 'is_spam', 'published_time')

    def get_children(self, parent):
        queryset = parent.get_children()
        serialized_data = CommentTreeSerializer(queryset, many=True, read_only=True, context=self.context)
        return serialized_data.data

    def create(self, validated_data):
        comment = Comment()
        comment.author = self.context['request'].user
        comment.content = validated_data['content']
        comment.content_type = validated_data['content_type']
        comment.object_id = validated_data['object_id']
        comment.parent = validated_data['parent']
        comment.save()

        #发送信号
        post_comment.send(sender=Comment, comment_obj = comment, content_type = validated_data['content_type'], object_id = validated_data['object_id'], request=self.context['request'])
        return comment