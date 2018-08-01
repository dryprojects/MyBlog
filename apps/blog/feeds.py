#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      feeds.py 
@time:      2018/05/02 
""" 

from django.contrib.syndication.views import Feed
from django.urls import reverse

from blog.models import Post
from blog import enums


class LatestPostFeed(Feed):
    """
    see more:
        https://docs.djangoproject.com/en/2.0/ref/contrib/syndication/
    """
    title = "最新博文 MyBlog"
    link = '/'
    description = 'MyBlog 最近更新的博文.'

    def items(self):
        return Post.objects.filter(status=enums.POST_STATUS_PUBLIC).order_by('-published_time')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt