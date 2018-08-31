#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      run.py 
@time:      2018/06/30
@desc:      爬虫启动脚本
"""

import collections

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import NotConfigured
from scrapy import signals

from scrapy_redis import connection, defaults
from redis import StrictRedis


class CrawlerScript:
    def __init__(self, spidercls: "list or dict"):
        """
        这里采用在一个crawler进程里运行多个spider线程的策略
        :param spidercls: 要启动的爬虫列表
        """
        self.spiders_mapping = collections.defaultdict(dict)
        if isinstance(spidercls, list):
            for spider in spidercls:
                self.spiders_mapping[spider] = {}
        elif isinstance(spidercls, dict):
            for spider, init_kwargs in spidercls.items():
                if not isinstance(init_kwargs, dict):
                    raise NotConfigured('爬虫初始化参数必须包含在字典里！')
                self.spiders_mapping[spider] = init_kwargs
        else:
            raise NotConfigured('spidercls参数必须是列表或者字典！')

        self.crawler_manager = CrawlerProcess(get_project_settings())

    def start(self, using_scrapy_redis=False):
        """
        启动crawler
        :return:
        """
        for spider_cls, init_kwargs in self.spiders_mapping.items():
            dfd = self.crawler_manager.crawl(spider_cls, **init_kwargs)  # 启动爬虫
            dfd.addCallbacks(self.spider_done, self.spider_error)

        if using_scrapy_redis:
            self.setup_redis(self.crawler_manager.crawlers)

        self.crawler_manager.start()  # 启动 reactor

    def setup_redis(self, crawlers):
        """
        当使用scrapy-redis时，启动爬虫时
        需要将各个爬虫的启始url设置到redis当中
        :return:
        """
        for crawler in crawlers:
            for start_url in crawler.spider.start_urls:
                crawler.spider.server.lpush(crawler.spider.redis_key, start_url)

    def spider_done(self, res):
        """
        爬虫正常结束后回调
        :param res:
        :return:
        """
        pass

    def spider_error(self, res, exc):
        """
        爬虫异常结束后回调
        :param res:
        :param exc:
        :return:
        """
        pass


if __name__ == "__main__":
    from robot.spiders.jobbole import JobboleSpider
    from robot.spiders.allitebooks import AllitebooksSpider
    from robot.spiders.proxy import ProxySpider

    CrawlerScript([ProxySpider]).start(using_scrapy_redis=True)
