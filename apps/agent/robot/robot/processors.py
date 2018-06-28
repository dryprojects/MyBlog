#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      processors.py 
@time:      2018/06/23 
"""

import hashlib
import re
import datetime
import time

import html2text


class TakeSecond(object):
    #loader processer 处理器，取list第二个元素
    def __call__(self, values):
        value = None
        try:
            if values[1] is not None and values[1] != "":
                value = values[1]
        except:
            pass
        return value


def FormatDateTime(value, formatter="%Y/%m/%d %H:%M:%S", out_formatter="%Y-%m-%d %H:%M:%S"):
    """
    将字符串日期value, 按照formatter格式转换为datetime类型，返回out_formatter格式的日期字符串
    """
    try:
        dt = datetime.datetime.strptime(value, formatter)
    except Exception as e:
        dt = datetime.datetime.now()
    try:
        dt = datetime.datetime.strftime(dt, out_formatter)
    except Exception as e:
        dt = datetime.datetime.now().strftime(out_formatter)

    return dt


def FormatTimestamp(value, formatter="%Y-%m-%d %H:%M:%S"):
    """
    将时间戳转换为指定格式的日期
    """
    try:
        dt = datetime.datetime.fromtimestamp(value).strftime(formatter)
    except Exception as e:
        dt = datetime.datetime.now().strftime(formatter)

    return dt


def RemoveSplash(value):
    #去掉‘/’
    return value.replace("/", "")


def RemoveSpace(value):
    #去掉文本中的空格和回车换行符
    value = value.strip()
    # value = re.sub(r"\r\n", "", value)
    return value


def ConvertToMd5(url):
    #获取url的md5摘要
    if isinstance(url, str): #如果是unicode则编码为utf8
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def ConvertToMarkDown(html):
    """
    将html转换为markdown格式
    """
    html = html.strip()
    return html2text.html2text(html)



def ExtractNumber(text):
    if text is None:
        return None
    #从文本中获取数字返回
    # xxx192,233,342xxx 形式或者 xxx123xxx这种形式
    match_re = re.match(r".*?((\d+,?){1,}).*|.*?(\d+).*", text)
    if match_re:
        #去掉字符串当中的','
        nums = re.sub(r",", "", match_re.group(1))
        nums = int(nums)
    else:
        nums = 0

    return nums