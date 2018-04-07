# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/26 22:28'

from django.urls import path, re_path
from blog.views import PostDetailView, PostListView, PostSearchView, PostAutoCompleteView

app_name = 'blog'
urlpatterns = [
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('', PostListView.as_view(), name='post-list'),
    path('search/', PostSearchView.as_view(), name='post-search'),
    path('auto/', PostAutoCompleteView.as_view(), name='post-autocomplete')
]