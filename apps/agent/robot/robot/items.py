# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import loader
from scrapy.loader import processors
from scrapy.loader.processors import MapCompose, TakeFirst, Join

from scrapy_djangoitem import DjangoItem

from blog.models import Post, Category, Tag
from bloguser.models import UserProfile

from django.db.transaction import atomic
from django.db.utils import IntegrityError

from robot import processors as proc


class JobboleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpaceForce)
    )
    cover_url = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpaceForce)
    )
    category = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpaceForce),
        output_processor = Join(',')
    )
    # 作者是scrapy_crawler
    author = scrapy.Field()
    content = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpace, proc.ConvertToMarkDown)
    )
    published_time = scrapy.Field()
    origin_post_url = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpaceForce)
    )
    origin_post_from = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpaceForce)
    )
    url_object_id = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpace, proc.ConvertToMd5)
    )

    def get_post_ref(self, **kwargs):
        # 创建一个名叫做scrapy的作者
        # 根据tags创建一个分类
        # 创建博文对应的标签
        tags = kwargs.pop('tags').split(',')
        category = None
        tag_list = []

        try:
            author = UserProfile.objects.get(username='ScrapyCrawler')
        except UserProfile.DoesNotExist:
            author = UserProfile()
            author.username = "ScrapyCrawler"
            author.email = "1045114396@qq.com"
            author.save()

        if len(tags) > 0:
            try:
                category = Category.objects.get(name=tags[0])
            except Category.DoesNotExist:
                category = Category()
                category.name = tags[0]
                category.save()

            for tag_name in tags:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    tag_list.append(tag)
                except Tag.DoesNotExist:
                    tag = Tag()
                    tag.name = tag_name
                    tag.save()
                    tag_list.append(tag)

        return (author, category, tag_list)


    def save(self, commit=True):
        with atomic():
            try:
                post = Post.objects.get(url_object_id=self['url_object_id'])
            except Post.DoesNotExist:
                # 博文不存在创建一个
                post = Post()
                post.cover_url = self['cover_url']
                post.origin_post_url = self['origin_post_url']
                post.origin_post_from = self['origin_post_from']
                post.url_object_id = self['url_object_id']
                post.title = self['title']
                post.content = self['content']
                post.published_time = self['published_time']

                author, category, tag_list = self.get_post_ref(tags=self['tags'])
                post.author = author
                post.category = category
                post.save()
                #在设置多对多之前需要先保存
                post.tags.set(tag_list)


class PostItemLoader(loader.ItemLoader):
    default_output_processor = processors.TakeFirst()


if __name__ == "__main__":
    pass
