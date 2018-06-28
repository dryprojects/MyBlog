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

from blog.models import Post

from robot import processors as proc


class JobboleItem(DjangoItem):
    # django_model = Post 这里需要覆写默认Post的字段
    title = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpace)
    )
    cover_url = scrapy.Field()
    category = scrapy.Field()
    tags = scrapy.Field()
    # 作者是scrapy_crawler
    author = scrapy.Field()
    content = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpace, proc.ConvertToMarkDown)
    )
    published_time = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpace)
    )
    origin_post_url = scrapy.Field()
    origin_post_from = scrapy.Field()
    url_object_id = scrapy.Field(
        input_processor=MapCompose(proc.RemoveSpace, proc.ConvertToMd5)
    )

    def save(self, commit=True):
        return super(JobboleItem, self).save(commit=commit)


class PostItemLoader(loader.ItemLoader):
    default_output_processor = processors.TakeFirst()


if __name__ == "__main__":
    pass
