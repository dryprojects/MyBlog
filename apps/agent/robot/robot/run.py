#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      run.py 
@time:      2018/06/30
@desc:      爬虫启动脚本
""" 


from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class CrawlerScript:
    def __init__(self, spidercls:list):
        """
        这里采用在一个crawler进程里运行多个spider线程的策略
        :param spidercls: 要启动的爬虫列表
        """
        self.spiders = spidercls
        self.crawler = CrawlerProcess(get_project_settings())

    def start(self):
        """
        启动crawler
        :return:
        """
        for spider in self.spiders:
            dfd = self.crawler.crawl(spider) #启动爬虫
            dfd.addCallbacks(self.spider_done, self.spider_error)

        self.crawler.start()           #启动 reactor

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

    CrawlerScript([ProxySpider]).start()