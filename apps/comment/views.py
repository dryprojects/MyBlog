from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework import permissions

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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('parent', 'content_type', 'object_id')

    @action(detail=True, methods=['post'])
    def like(self, request, pk, *args, **kwargs):
        comment_obj = self.get_object()
        comment_obj.n_like += 1
        comment_obj.save()

        #发送点赞信号
        post_like.send(sender=Comment, comment_obj=comment_obj, content_type = comment_obj.content_type, object_id = comment_obj.object_id)
        serializer = self.get_serializer(comment_obj)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def dislike(self, request, pk, *args, **kwargs):
        comment_obj = self.get_object()
        comment_obj.n_like -= 1
        comment_obj.save()

        serializer = self.get_serializer(comment_obj)
        return Response(serializer.data)

