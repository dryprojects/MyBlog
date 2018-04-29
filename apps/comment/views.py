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
    queryset = Comment.objects.all()
    serializer_class = CommentTreeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    @action(detail=True, methods=['post'])
    def like(self, request, pk, *args, **kwargs):
        comment_obj = self.get_object()
        comment_obj.n_like += 1
        comment_obj.save()

        serializer = self.get_serializer(comment_obj)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def dislike(self, request, pk, *args, **kwargs):
        comment_obj = self.get_object()
        comment_obj.n_like -= 1
        comment_obj.save()

        serializer = self.get_serializer(comment_obj)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        返回各个根评论
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset().filter(parent=None))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)