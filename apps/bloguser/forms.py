#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      forms.py 
@time:      2018/05/04 
"""

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django import forms
from django import db

from bloguser.models import UserProfile
from bloguser.tasks import send_mail

from captcha.fields import CaptchaField


class BlogUserCreationForm(UserCreationForm):
    """
    for user register
    这里采用邮箱注册。
    """
    email = forms.EmailField(required=True)
    captcha = CaptchaField()

    class Meta:
        model = UserProfile
        fields = ['email', 'password1', 'password2', 'captcha']

    def async_send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):

        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        send_mail.delay(subject, body, from_email, to_email)

    def get_context_data(self, **kwargs):
        context = {}
        request = kwargs.pop('request')
        user = kwargs.pop('user')
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        context = {
            'email':kwargs.pop('email'),
            'site_name':site_name,
            'domain':domain,
            'protocol': 'https' if request.is_secure() else 'http',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'user': user,
            'token': default_token_generator.make_token(user),
        }
        return context

    def save(self, commit=True, subject_template_name='bloguser/register_active_subject.txt',
             email_template_name='bloguser/register_active_email.html', request=None):
        try:
            user = super().save(commit=False)
        except db.IntegrityError as e:
            raise forms.ValidationError(repr(e))

        user.is_active = False
        email = self.cleaned_data["email"]
        user.username = email
        if commit:
            user.save()

        # 给用户发送激活帐号的邮件
        context = self.get_context_data(email=email, request=request, user=user)

        self.async_send_mail(subject_template_name, email_template_name, context, from_email=None, to_email=[email])
        return user


class BlogUserChangeForm(UserChangeForm):
    """
    for update user info
    """

    class Meta:
        model = UserProfile
        exclude = ['image_url']
