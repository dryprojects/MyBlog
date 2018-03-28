import datetime

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.urls import reverse

# Create your models here.
User = get_user_model()

class Comment(models.Model):
    content = models.TextField(verbose_name='评论内容')
    author = models.ForeignKey(User, verbose_name='评论者', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, verbose_name='评论附加对象的ct类型', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(verbose_name='评论附加对象id')
    content_object = GenericForeignKey('content_type', 'object_id') #被评论附加的对象
    published_time = models.DateTimeField(verbose_name='评论时间', default=datetime.datetime.now)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        app_label = 'comment'

    def content_object_name(self):
        model = self.content_type.model_class()
        object = model.objects.filter(pk=self.object_id)[0]
        return str(object)
    content_object_name.short_description = '评论附加对象'

    @property
    def title(self):
        return "%s评论"%self.content_type

    def __str__(self):
        return self.content[:20]

"""
查询某一篇博客的所有评论
post = Post.objects.all().get(..)
post_ct = ContentType.object.get_for_model(Post)
Comment.object.filter(content_type__pk=post_ct.id, object_id=post.id)
"""