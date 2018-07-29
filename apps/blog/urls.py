# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/26 22:28'

from django.urls import path, re_path, include
from django.conf import settings

from rest_framework.routers import DefaultRouter

from blog import views
from blog.api import views as api_views
from blog import feeds


API_MODE = settings.API_MODE


app_name = 'blog'

if not API_MODE:
    urlpatterns = [
        path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
        path('', views.PostListView.as_view(), name='post-list'),
        path('search/', views.PostSearchView.as_view(), name='post-search'),
        path('auto/', views.PostAutoCompleteView.as_view(), name='post-autocomplete'),
        path('latest/post/', feeds.LatestPostFeed(), name='post-latest'),
        path('archive/<int:year>/<int:month>/', views.PostArchiveListView.as_view(), name='post-archive'),
        path('tag/<int:pk>/', views.PostTagListView.as_view(), name='post-tag'),
        path('category/<int:pk>/', views.PostCategoryListView.as_view(), name='post-category'),
        path('thumb/<int:pk>/', views.PostThumbView.as_view(), name='post-thumb'),
        path('about/', views.BlogAbout.as_view(), name='blog-about'),
        # path('export/', views.ExportPostView.as_view(), name='export-post')
    ]
else:
    router = DefaultRouter()
    router.register('posts', api_views.PostReadOnlyViewset, base_name='post')
    router.register('categories', api_views.CategoryViewset, base_name='category')
    router.register('tags', api_views.TagViewset, base_name='tag')
    router.register('resources', api_views.ResourceViewset, base_name='resource')

    urlpatterns = [
        path('', include(router.urls))
    ]