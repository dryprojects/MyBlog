#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      tests.py 
@time:      2018/08/30 
""" 
import os

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.phantomjs.webdriver import WebDriver
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType


project_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

options = Options()
options.add_argument('-headless')   #去掉浏览器界面 （firefox）
                                    # chrome去掉界面请设置 '--headless' 和 '--disable-gpu' 选项
driver = WebDriver(
    executable_path=os.path.join(project_base, 'tools/browser_driver/firefox/linux64/geckodriver'),
    firefox_options=options
)

if __name__ == '__main__':
    print(project_base)
    driver.get('http://www.baidu.com')
    print(driver.page_source)