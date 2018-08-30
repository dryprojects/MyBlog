# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os


class DjangoPipeline(object):
    def process_item(self, item, spider):
        if spider.name != 'proxy':
            item.save()
        return item


class ProxyWriterPipeline(object):
    def __init__(self, crawler):
        super(ProxyWriterPipeline, self).__init__()
        default_base_dir = os.path.dirname(__file__)
        self.base_dir = crawler.settings.get("BASE_DIR", default_base_dir)
        self.proxy_dir_name = crawler.settings.get("PROXY_DIR_NAME", os.path.join(self.base_dir, 'proxy'))
        self.file_name = crawler.settings.get("PROXY_FILE_NAME", 'proxy_list.txt')

        if not os.path.exists(self.proxy_dir_name):
            os.mkdir(os.path.join(self.base_dir, self.proxy_dir_name))

    def open_spider(self, spider):
        self.file = open(os.path.join(self.base_dir, self.proxy_dir_name, self.file_name), 'w')

    def close_spider(self, spider):
        self.file.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        if spider.name == 'proxy':
            line = "{proxy_type}://{host}:{port}\n".format(
                proxy_type=item.get('proxy_type'),
                host=item.get('host'),
                port=item.get('port'))

            self.file.write(line)

        return item
