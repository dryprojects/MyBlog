#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      fields.py 
@time:      2018/05/01 
""" 

from django import forms
from django.db import models

from mdeditor.widgets import MdTextWidget


class MdTextFormField(forms.fields.CharField):
    """ custom form field """
    def __init__(self, config_name='default', *args, **kwargs):
        kwargs.update({
            'widget': MdTextWidget(config_name=config_name)
        })
        super(MdTextFormField, self).__init__(*args, **kwargs)


class MdTextField(models.TextField):
    """ custom model field """

    def __init__(self, *args, **kwargs):
        self.config_name = kwargs.pop("config_name", "default")
        super(MdTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': MdTextFormField,
            'config_name': self.config_name
        }
        defaults.update(kwargs)
        return super(MdTextField, self).formfield(**defaults)