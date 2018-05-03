# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/26 22:28'

from django.urls import path, re_path
from blog import views
from blog import feeds


app_name = 'blog'

urlpatterns = [
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('', views.PostListView.as_view(), name='post-list'),
    path('search/', views.PostSearchView.as_view(), name='post-search'),
    path('auto/', views.PostAutoCompleteView.as_view(), name='post-autocomplete'),
    path('latest/post/', feeds.LatestPostFeed(), name='post-latest'),
    path('archive/<int:year>/<int:month>/', views.PostArchiveView.as_view(), name='post-archive')
]