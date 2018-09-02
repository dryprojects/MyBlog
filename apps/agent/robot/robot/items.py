# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re
import os
import requests
import uuid

import scrapy
from scrapy import loader
from scrapy.loader import processors
from scrapy.loader.processors import MapCompose, TakeFirst, Join, Identity
from scrapy.exceptions import DropItem

from scrapy_djangoitem import DjangoItem

from blog.models import Post, Category, Tag
from bloguser.models import UserProfile
from ebooks.models import Ebook

from django.db.transaction import atomic
from django.db.utils import IntegrityError
from django.core.files.base import ContentFile

from robot import processors as proc


def RemoveTagComment(tag_name:str):
    #去除jobbole博文标签里的 ‘评论’
    if "评论" in tag_name:
        return ""
    else:
        return tag_name


def RemovePostAdd(html:"html text"):
    #去除jobbole博文里附加的内容
    #<div class="post-adds"></div>
    html = re.sub(r'<div class="post-adds">.*</div>', "", html, flags=re.S)
    return html


class JobboleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpaceForce)
    )
    cover_url = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpaceForce)
    )
    category = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpaceForce, RemoveTagComment),
        output_processor = Join(',')
    )
    # 作者是scrapy_crawler
    author = scrapy.Field()
    content = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpace, RemovePostAdd, proc.ConvertToMarkDown)
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
            author.email = "scrapy@scrapycrawler.com"
            author.set_password("ScrapyCrawler")
            author.save()

        if len(tags) > 0:
            try:
                category = Category.objects.get(name=tags[0])
            except Category.DoesNotExist:
                category = Category()
                category.name = tags[0]
                category.author = author
                category.save()

            for tag_name in tags:
                if tag_name != "":
                    try:
                        tag = Tag.objects.get(name=tag_name)
                        tag_list.append(tag)
                    except Tag.DoesNotExist:
                        tag = Tag()
                        tag.name = tag_name
                        tag.author = author
                        tag.save()
                        tag_list.append(tag)

        return (author, category, tag_list)

    def get_image_from_url(self, url):
        """
        这里把博文图片保存到本地数据库
        :param url:
        :return:
        """
        response = requests.get(url)
        if response.status_code == 200:
            img_file = ContentFile(response.content)
            return img_file

        return None

    def get_cover_name(self, url):
        if url:
            ext = os.path.splitext(url)[1]
            if ext:
                return uuid.uuid4().hex + ext
        return uuid.uuid4().hex

    def save(self, commit=True):
        with atomic():
            try:
                post = Post.objects.get(url_object_id=self['url_object_id'])
                post.content = self['content']
                post.published_time = self['published_time']
                post.save()
                post.cover.save(self.get_cover_name(self['cover_url']), self.get_image_from_url(self['cover_url']))
            except Post.DoesNotExist:
                # 博文不存在创建一个
                post = Post()
                post.origin_post_url = self.get('origin_post_url', "")
                post.origin_post_from = self['origin_post_from']
                post.url_object_id = self['url_object_id']
                post.title = self['title']
                post.content = self['content']
                post.published_time = self['published_time']

                author, category, tag_list = self.get_post_ref(tags=self['tags'])
                post.author = author
                post.category = category
                post.save()
                post.cover.save(self.get_cover_name(self['cover_url']), self.get_image_from_url(self['cover_url']))
                #在设置多对多之前需要先保存
                post.tags.set(tag_list)


class AllitebooksItem(scrapy.Item):
    title = scrapy.Field()
    sub_title = scrapy.Field()
    cover_url = scrapy.Field()
    author_name = scrapy.Field()
    isbn = scrapy.Field()
    published_year = scrapy.Field()
    pages = scrapy.Field()
    language = scrapy.Field()
    file_size = scrapy.Field()
    file_format = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpace, proc.ConvertToMarkDown),
        output_processor=Join("\n")
    )
    download_links = scrapy.Field(
        output_processor=Join('|')
    )
    url_object_id = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpace, proc.ConvertToMd5)
    )

    def save(self, commit=True):
        with atomic():
            ebook, created = Ebook.objects.get_or_create(
                url_object_id=self.get("url_object_id", ""),
                defaults={
                    "title": self.get("title", ""),
                    "sub_title": self.get("sub_title", ""),
                    "cover_url": self.get("cover_url", ""),
                    "author_name": self.get("author_name", ""),
                    "isbn": self.get("isbn", ""),
                    "published_year": self.get("published_year", ""),
                    "pages": self.get("pages", ""),
                    "language": self.get("language", ""),
                    "file_size": self.get("file_size", ''),
                    "file_format": self.get("file_format", ''),
                    "category": self.get("category", ""),
                    "description":self.get("description", ""),
                    "download_links":self.get("download_links", ""),
                }
            )

            if created:
                ebook.description = self.get("description", "")
                ebook.save()


class ProxyItem(scrapy.Item):
    port = scrapy.Field()
    anonymity = scrapy.Field()
    high_anonymous = scrapy.Field()
    proxy_from = scrapy.Field()
    proxy_type = scrapy.Field()
    response_time = scrapy.Field()
    host = scrapy.Field()
    country = scrapy.Field()
    export_address = scrapy.Field(
        output_processor=Join("\n")
    )


class PostItemLoader(loader.ItemLoader):
    default_output_processor = processors.TakeFirst()


class AllitebooksItemLoader(loader.ItemLoader):
    default_output_processor = processors.TakeFirst()


class ProxyItemLoader(loader.ItemLoader):
    default_output_processor = processors.TakeFirst()


if __name__ == "__main__":
    pass
