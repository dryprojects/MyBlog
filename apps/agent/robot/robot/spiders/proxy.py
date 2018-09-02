# -*- coding: utf-8 -*-
import json

import scrapy

from robot.items import ProxyItem, ProxyItemLoader
from robot.processors import RemoveTags

from scrapy_redis.spiders import RedisSpider


class ProxySpider(RedisSpider):
    name = 'proxy'
    allowed_domains = ['raw.githubusercontent.com']
    start_urls = ['https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list']

    def parse(self, response):
        """
        解析ip代理
        :param response:
        :return:
        """
        proxy_list = RemoveTags(response.text).splitlines()

        for proxy in proxy_list:
            item_loader = ProxyItemLoader(item=ProxyItem(), response=response)
            proxy = json.loads(proxy)
            item_loader.add_value("port", proxy.get("port", ""))
            item_loader.add_value("anonymity", proxy.get("anonymity", ""))
            item_loader.add_value("proxy_from", proxy.get("from", ""))
            item_loader.add_value("proxy_type", proxy.get("type", ""))
            item_loader.add_value("response_time", proxy.get("response_time", ""))
            item_loader.add_value("host", proxy.get("host", ""))
            item_loader.add_value("country", proxy.get("country", ""))
            item_loader.add_value("export_address", proxy.get("export_address", ""))

            proxy_item = item_loader.load_item()
            yield proxy_item