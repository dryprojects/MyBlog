# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/7 14:03'

from datetime import datetime

from haystack import indexes

from blog.models import Post
from blog import enums


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)          # 全文检索字段
    title_auto = indexes.EdgeNgramField(model_attr='title')             # 该字段用与搜索建议
    author = indexes.CharField(model_attr='author', faceted=True)       # author 和 pub_date 用于额外对搜索集合过滤
    pub_date = indexes.DateTimeField(model_attr='published_time')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        """
        只索引今天之前发表的博文
        :param using:
        :return:
        """
        return self.get_model().objects.filter(published_time__lte=datetime.now(), status=enums.POST_STATUS_PUBLIC, post_type=enums.POST_TYPE_POST)
