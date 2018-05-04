#!usr/bin/env python  
#-*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      forms.py 
@time:      2018/05/04 
""" 

from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

from bloguser.models import UserProfile

from captcha.fields import CaptchaField


class BlogUserCreationForm(UserCreationForm):
    """
    for user register
    """
    class Meta:
        model = UserProfile
        fields = UserCreationForm.Meta.fields + ('image', )


class BlogUserChangeForm(UserChangeForm):
    """
    for update user info
    """
    class Meta:
        model = UserProfile
        fields = '__all__'


class BlogUserAuthenticationForm(AuthenticationForm):
    """
    for user login
    """
    captcha = CaptchaField()