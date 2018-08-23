from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions

from django.db.models import F
from django.contrib.contenttypes.models import ContentType

from django_filters import rest_framework as filters
from rest_framework_extensions.mixins import NestedViewSetMixin

from comment.serializers import CommentTreeSerializer, ContentTypeSerializer, ReplySerializer
from comment.models import Comment
from comment.permissions import IsOwnerOrReadOnly
from comment.signals import post_like
from comment import filters as cmt_filters
from comment.throttling import CommentThrotting


class CommentViewset(NestedViewSetMixin, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    list:
        返回所有用户所有类型的评论/回复
    retrieve:
        返回指定的一条评论/回复
    create:
        创建给定类型和对象的一条评论/回复
    destroy:
        只有作者可以删除评论/回复
    """
    queryset = Comment.objects.all()
    serializer_class = CommentTreeSerializer
    throttle_classes = (CommentThrotting,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = cmt_filters.CommentFilter

    def get_permissions(self):
        """
        对不同的操作设置不同权限
        action:
            list                IsAuthenticated
            create              IsAuthenticated
            retrieve            IsAuthenticated
            destroy             IsOwnerOrReadOnly
            like                IsAuthenticated
            cancel_like         IsAuthenticated
        :return:
        """
        if self.action in ['destroy', 'list']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def check_allow_reply(self, content_type, object_id, parent):
        """
        检查是否可以对评论回复
        :param content_type:
        :param object_id:
        :return:
        """
        cmt_content_type = ContentType.objects.get_for_model(Comment)
        if content_type == cmt_content_type:
            #如果是评论回复，则需要检测根评论的附加内容对象是否允许发表评论
            root = parent.get_root()
            checked = getattr(root.content_object, "allow_post_comment", False)

            if not checked:
                return False

        return True

    def perform_create(self, serializer):
        """
        判断是否有权限进行评论
        被评论的对象，要实现allow_post_comment属性
        :param serializer:
        :return:
        """
        validated_data = serializer.validated_data
        content_type = validated_data.get('content_type', None)
        object_id = validated_data.get('object_id', None)

        if content_type and object_id:
            parent = validated_data.get('parent', None)
            object = content_type.get_object_for_this_type(id=object_id)

            checked = getattr(object, "allow_post_comment", False) and self.check_allow_reply(content_type, object_id,
                                                                                              parent)

            if not checked:
                self.permission_denied(self.request, "你没有权限发表评论")

        # 有可能内容类型已经知道， 这时需要自己实现对应类型的评论权限检测
        serializer.save()

    @action(detail=True, methods=['post'])
    def like(self, request, pk, *args, **kwargs):
        comment_obj = self.get_object()
        comment_obj.n_like = F('n_like') + 1
        comment_obj.save()

        # 发送点赞信号
        post_like.send(sender=Comment, comment_obj=comment_obj, content_type=comment_obj.content_type,
                       object_id=comment_obj.object_id, request=self.request)
        # 使用F表达式后需要重新求值
        comment_obj = self.get_object()
        serializer = self.get_serializer(comment_obj)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel_like(self, request, pk, *args, **kwargs):
        comment_obj = self.get_object()
        comment_obj.n_like = F('n_like') - 1
        comment_obj.save()

        comment_obj = self.get_object()
        serializer = self.get_serializer(comment_obj)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_content_type(self, request):
        """list: 返回评论的内容类型id"""
        content_type = ContentType.objects.get_for_model(Comment)
        serializer = ContentTypeSerializer(content_type)
        return Response(serializer.data)


class ReplyViewSet(CommentViewset):
    serializer_class = ReplySerializer

    def get_queryset(self):
        return super().get_queryset().filter(
            content_type=ContentType.objects.get_for_model(Comment)
        )
