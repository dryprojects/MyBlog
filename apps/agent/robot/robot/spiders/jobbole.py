# -*- coding: utf-8 -*-
import urllib

import scrapy
from scrapy.http import Request

from robot.items import PostItemLoader, JobboleItem


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页的url, 并交给scrapy下载后并由自定义解析函数进行具体字段的处理
        2. 获取下一页的url并交给scrapy进行下载
        :param response:
        :return:
        """
        #解析列表页中的所有文章url并交给scrapy下载后进行解析

        post_list = response.css("#archive .floated-thumb .post-thumb a")
        for post in post_list:
            post_cover = urllib.parse.urljoin(response.url, post.css("img::attr(src)").extract_first(""))
            post_detail = post.css('::attr(href)').extract_first("")
            yield Request(url=urllib.parse.urljoin(response.url, post_detail), callback=self.parse_post_detail, meta={'post_cover':post_cover})

        #提取下一页并交给scrapy下载
        next_page = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_page:
            yield Request(url=urllib.parse.urljoin(response.url, next_page), callback=self.parse)

    def parse_post_detail(self, response):
        """
        解析文章详情
        :param response:
        :return:
        """
        cover_url = response.meta.get('post_cover', '')
        #通过itemloader加载item
        item_loader = PostItemLoader(item=JobboleItem(), response=response)
        item_loader.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        item_loader.add_value('cover_url', [cover_url])
        item_loader.add_xpath('origin_post_url', '//div[@class="copyright-area"]/a/@href')
        item_loader.add_xpath('origin_post_from', '//div[@class="copyright-area"]/a/text()')
        item_loader.add_value('url_object_id', [response.url])
        item_loader.add_xpath('published_time', '//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_xpath('content', '//div[@class="entry"]')
        item_loader.add_xpath('tags', '//p[@class="entry-meta-hide-on-mobile"]/a/text()')

        article_item = item_loader.load_item()

        yield article_item