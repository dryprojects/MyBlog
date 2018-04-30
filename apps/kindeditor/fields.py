#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      fields.py 
@time:      2018/04/30 
""" 

from django import forms
from django.db import models

from kindeditor.widgets import KindTextareaWidget


class KindFormTextField(forms.fields.CharField):
    def __init__(self, config, *args, **kwargs):
        kwargs.update(
            {
                'widget':KindTextareaWidget(config=config)
            }
        )
        super(KindFormTextField, self).__init__(*args, **kwargs)


class KindModelTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop('config', {})
        super(KindModelTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': KindFormTextField,
            'config':self.config
        }
        defaults.update(kwargs)
        return super(KindModelTextField, self).formfield(**defaults)