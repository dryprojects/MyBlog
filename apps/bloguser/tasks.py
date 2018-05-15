#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      tasks.py 
@time:      2018/05/06 
""" 
from django.core.mail import send_mail as _send_mail

from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task(bind=True)
def send_mail(self, subject, message, from_email, recipient_list, html_msg=None):
    _send_mail(subject, message, from_email, recipient_list, html_message=html_msg)