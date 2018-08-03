#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      sitemaps.py 
@time:      2018/06/17 
""" 

from django.contrib.sitemaps import Sitemap

from blog.models import Post


class BlogSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Post.objects.filter(status='published', post_type='post')

    def lastmod(self, obj):
        return obj.published_time