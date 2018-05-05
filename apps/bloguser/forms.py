#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      forms.py 
@time:      2018/05/04 
""" 

from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from bloguser.models import UserProfile

from captcha.fields import CaptchaField


class BlogUserCreationForm(UserCreationForm):
    """
    for user register
    """
    captcha = CaptchaField()

    class Meta:
        model = UserProfile
        fields = UserCreationForm.Meta.fields + ('image', )


class BlogUserChangeForm(UserChangeForm):
    """
    for update user info
    """
    class Meta:
        model = UserProfile
        exclude = ['image_url']