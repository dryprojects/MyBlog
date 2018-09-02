#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      schedulers.py 
@time:      2018/09/02 
"""

from scrapy.utils.misc import load_object

from scrapy_redis import scheduler as redis_scheduler
from  scrapy.core import scheduler


class RedisScheduler(redis_scheduler.Scheduler):
    def open(self, spider):
        self.spider = spider

        try:
            self.queue = load_object(self.queue_cls)(
                server=self.server,
                spider=spider,
                key=self.queue_key % {'spider': spider.name},
                serializer=self.serializer,
            )
        except TypeError as e:
            raise ValueError("Failed to instantiate queue class '%s': %s",
                             self.queue_cls, e)

        try:
            self.df = load_object(self.dupefilter_cls)(
                capacity=spider.settings.get("BLOOMFILTER_REDIS_CAPACITY", 100000000),
                error_rate=spider.settings.get("BLOOMFILTER_REDIS_FALSE_POSITIVE_PROBABILITY", 0.0001),
                server=self.server,
                key_prefix=self.dupefilter_key % {'spider': spider.name},
                block_nums=spider.settings.get("BLOOMFILTER_REDIS_BLOCK_NUMS", 1),
                debug=spider.settings.getbool('DUPEFILTER_DEBUG'),
            )
        except TypeError as e:
            raise ValueError("Failed to instantiate dupefilter class '%s': %s",
                             self.dupefilter_cls, e)

        if self.flush_on_start:
            self.flush()
        # notice if there are requests already in the queue to resume the crawl
        if len(self.queue):
            spider.log("Resuming crawl (%d requests scheduled)" % len(self.queue))
