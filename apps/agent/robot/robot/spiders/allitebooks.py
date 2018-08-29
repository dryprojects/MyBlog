# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.linkextractors import LinkExtractor

from urllib.parse import urljoin


from robot.items import AllitebooksItem, AllitebooksItemLoader


class AllitebooksSpider(scrapy.Spider):
    name = 'allitebooks'
    allowed_domains = ['www.allitebooks.com']
    start_urls = ['http://www.allitebooks.com/']

    def parse(self, response):
        book_list = response.css(".main-content-inner article")
        for book in book_list:
            book_detail = book.css('.entry-thumbnail a::attr(href)').extract_first("")
            yield Request(url=urljoin(response.url, book_detail), callback=self.parse_book_detail)

        next_page = response.css(".pagination .current+a::attr(href)").extract_first("")
        if next_page:
            yield Request(url=urljoin(response.url, next_page), callback=self.parse)

    def parse_book_detail(self, response):
        #通过itemloader加载item
        item_loader = AllitebooksItemLoader(item=AllitebooksItem(), response=response)
        item_loader.add_xpath('title', '//article/header/h1/text()')
        item_loader.add_xpath('sub_title', '//article/header/h4/text()')
        item_loader.add_xpath('cover_url', '//article/header/div[contains(@class, "entry-meta")]/div[contains(@class, "entry-body-thumbnail")]/a/img/@src')
        item_loader.add_xpath('author_name', '//article/header/div[contains(@class, "entry-meta")]/div[contains(@class, "book-detail")]//dd[1]/a/text()')
        item_loader.add_xpath('isbn', '//article/header/div[contains(@class, "entry-meta")]/div[contains(@class, "book-detail")]//dd[2]/text()')
        item_loader.add_xpath('published_year', '//article/header/div[contains(@class, "entry-meta")]/div[contains(@class, "book-detail")]//dd[3]/text()')
        item_loader.add_xpath('pages', '//article/header/div[contains(@class, "entry-meta")]/div[contains(@class, "book-detail")]//dd[4]/text()')
        item_loader.add_xpath('language', '//article/header/div[contains(@class, "entry-meta")]/div[contains(@class, "book-detail")]//dd[5]/text()')
        item_loader.add_xpath('file_size', '//article/header/div[contains(@class, "entry-meta")]/div[contains(@class, "book-detail")]//dd[6]/text()')
        item_loader.add_xpath('file_format', '//article/header/div[contains(@class, "entry-meta")]/div[contains(@class, "book-detail")]//dd[7]/text()')
        item_loader.add_xpath('category', '//article/header/div[contains(@class, "entry-meta")]/div[contains(@class, "book-detail")]//dd[8]/a/text()')
        item_loader.add_xpath('description', '//article/div[@class="entry-content"]/h3/following-sibling::*')
        item_loader.add_xpath('download_links', '//article/footer/div[contains(@class, "entry-meta")]/*[contains(@class, "download-links")]/a/@href')
        item_loader.add_value('url_object_id', [response.url])

        book_item = item_loader.load_item()

        yield book_item