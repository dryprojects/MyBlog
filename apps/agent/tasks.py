#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      tasks.py 
@time:      2018/06/23 
""" 

import os

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True)
def post_crawler(self):
    from agent.robot.robot.spiders.jobbole import JobboleSpider
    from agent.robot.robot.run import CrawlerScript

    os.environ['SCRAPY_SETTINGS_MODULE'] = 'agent.robot.robot.settings'
    logger.info(os.environ['SCRAPY_SETTINGS_MODULE'])

    CrawlerScript([JobboleSpider]).start()