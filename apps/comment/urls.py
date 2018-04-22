# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/22 11:06'

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from comment.views import CommentViewset


app_name = 'comment'

router = DefaultRouter()
router.register('', CommentViewset, base_name='comment')

urlpatterns = [
    path('', include(router.urls)),
]