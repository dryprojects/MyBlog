# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/4/7 14:03'

from datetime import datetime

from haystack import indexes

from blog.models import Post
from blog import enums


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title_auto = indexes.EdgeNgramField(model_attr='title')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        """
        只索引今天之前发表的博文
        :param using:
        :return:
        """
        return self.get_model().objects.filter(published_time__lte=datetime.now(), status=enums.POST_STATUS_PUBLIC, post_type=enums.POST_TYPE_POST)
