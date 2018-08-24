# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/22 11:06'

from django.urls import path, include
from rest_framework_extensions.routers import ExtendedDefaultRouter as DefaultRouter

from comment.views import CommentViewset, ReplyViewSet


app_name = 'comment'

router = DefaultRouter()
router.register('', CommentViewset, base_name='comment')\
    .register('reply', ReplyViewSet, base_name='reply', parents_query_lookups=['object_id'])

urlpatterns = [
    path('', include(router.urls)),
]