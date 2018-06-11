#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      context_processors.py 
@time:      2018/05/03 
""" 

from blog.models import Post, Tag, Category
from oper.models import BlogOwner, FriendshipLinks


def post_extra(request):
    context = {}
    post_queryset = Post.objects.filter(status='published')
    #按月份归档
    post_archive_date_list = post_queryset.dates('published_time', 'month', order='DESC')
    context['post_archive_date_list'] = post_archive_date_list
    #所有博文的标签
    post_tag_list = Tag.objects.all()
    context['post_tag_list'] = post_tag_list
    #所有的博文分类
    cts = Category.objects.all()
    context['post_category_list'] = cts
    #点赞最多的 点赞数排序
    post_thumb_most_list = post_queryset.filter(type='post').order_by('-n_praise')[:3]
    context['post_thumb_most_list'] = post_thumb_most_list
    #热门博文 浏览数排序
    hot_posts = post_queryset.filter(type='post').order_by('-n_browsers')[:3]
    context['hot_posts'] = hot_posts
    #博主推荐
    blogowner = BlogOwner.objects.first()
    if blogowner is not None:
        recommend_posts = blogowner.recommend_posts.all()
    else:
        recommend_posts = []
    context['recommend_posts'] = recommend_posts
    #友情链接
    friendship_links = FriendshipLinks.objects.all()[:10]
    context['friendship_links'] = friendship_links
    #公告
    blog_notifications = post_queryset.filter(type='notification')[:3]
    context['blog_notifications'] = blog_notifications
    #博主信息
    context['blog_owner'] = blogowner
    #轮播
    post_banners = post_queryset.filter(status='published', type='post', is_banner=True)[:5]
    context['post_banners'] = post_banners

    return context