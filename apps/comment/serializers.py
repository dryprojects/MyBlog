# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/22 11:12'

from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers, exceptions

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
        comment.parent = validated_data.get('parent', None)
        comment.save()

        # 发送信号
        post_comment.send(sender=Comment, comment_obj=comment, content_type=validated_data['content_type'],
                          object_id=validated_data['object_id'], request=self.context['request'])
        return comment


class ReplySerializer(CommentTreeSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta(CommentTreeSerializer.Meta):
        fields = ['id', 'parent', 'content', 'author', 'published_time', 'n_like', 'n_dislike', 'is_spam', 'children']
        extra_kwargs = {
            'parent': {'read_only': True}
        }

    def create(self, validated_data):
        content_type = ContentType.objects.get_for_model(Comment)
        object_id = self.context['view'].kwargs['parent_lookup_object_id']
        obj = content_type.get_object_for_this_type(id=object_id)

        if not self.check_allow_post_comment(obj):
            raise exceptions.PermissionDenied(detail='你不能对该评论进行回复。')

        validated_data.update(
            content_type=content_type,
            object_id=object_id,
            parent=obj,
        )
        return super().create(validated_data)

    def check_allow_post_comment(self, obj):
        return getattr(obj, "allow_post_comment", False)


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ('id',)
