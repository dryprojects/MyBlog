# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from robot.spiders.allitebooks import AllitebooksSpider
from robot.spiders.jobbole import JobboleSpider

spider_list = [AllitebooksSpider, JobboleSpider]