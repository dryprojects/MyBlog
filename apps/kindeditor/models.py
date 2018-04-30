from django.db import models

# Create your models here.

class ImageUpload(models.Model):
    imgFile = models.ImageField(verbose_name='kindeditor上传的图片', upload_to='kindeditor/images/%Y/%m', max_length=200)
