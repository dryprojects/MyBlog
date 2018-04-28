from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework import permissions

from comment.serializers import CommentTreeSerializer
from comment.models import Comment
from comment.permissions import IsOwnerOrReadOnly


class CommentViewset(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    additionally also provide an extra praise action
    """
    queryset = Comment.objects.filter(parent=None)
    serializer_class = CommentTreeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    @action(detail=True, methods=['post'])
    def like(self, request, pk, *args, **kwargs):
        comment_obj = self.get_object()
        pass

    @action(detail=True, methods=['post'])
    def dislike(self, request, pk, *args, **kwargs):
        comment_obj = self.get_object()
        pass