from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions
from django.db.models import F

from django_filters import rest_framework as filters

from comment.serializers import CommentTreeSerializer
from comment.models import Comment
from comment.permissions import IsOwnerOrReadOnly
from comment.signals import post_like


class CommentViewset(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    additionally also provide an extra praise action
    """
    queryset = Comment.objects.all()
    serializer_class = CommentTreeSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('parent', 'content_type', 'object_id')

    def get_permissions(self):
        """
        对不同的操作设置不同权限
        action:
            list                IsAuthenticatedOrReadOnly
            create              IsAuthenticatedOrReadOnly
            retrieve            IsAuthenticatedOrReadOnly
            update              IsOwnerOrReadOnly
            partial_update      IsOwnerOrReadOnly
            destroy             IsOwnerOrReadOnly
            like                IsAuthenticatedOrReadOnly
            cancel_like         IsAuthenticatedOrReadOnly
        :return:
        """
        if self.action in ['destroy', 'update', 'partial_update']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def like(self, request, pk, *args, **kwargs):
        comment_obj = self.get_object()
        comment_obj.n_like = F('n_like') + 1
        comment_obj.save()

        #发送点赞信号
        post_like.send(sender=Comment, comment_obj=comment_obj, content_type = comment_obj.content_type, object_id = comment_obj.object_id, request=self.request)
        #使用F表达式后需要重新求值
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

