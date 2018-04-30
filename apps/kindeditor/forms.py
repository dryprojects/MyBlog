# -*- coding:utf-8 -*-
__author__ = 'Ren Kang'
__date__ = '2018/3/31 15:47'

from django import forms

from kindeditor.models import ImageUpload


class ImageFileForm(forms.ModelForm):
    """
    验证上传的图片
    """
    class Meta:
        model = ImageUpload
        fields = '__all__'
        error_messages = {
            'imgFile':{
                'required':'上传图片不能为空'
            }
        }
