import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from blog.models import Post
# Create your models here.

User = get_user_model()


class Notification(models.Model):
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, default=0)
    content = models.TextField(verbose_name='消息')
    has_read = models.BooleanField(verbose_name='是否已读', default=False)
    published_time = models.DateTimeField(verbose_name='添加时间', default=datetime.datetime.now)

    class Meta:
        verbose_name = '站内通知'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "(%s):%s"%(self.id, self.content[:20])


class NotificationUnReadCounter(models.Model):
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, default=0)
    n_unread = models.PositiveIntegerField(verbose_name='未读数量', default=0)

    class Meta:
        verbose_name = '未读消息计数器'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "(%s):%s"%(self.id, self.n_unread)


class BlogOwner(models.Model):
    user = models.ForeignKey(User, verbose_name='博主', on_delete=models.CASCADE, default=0)
    qq = models.CharField(verbose_name='QQ', max_length=15)
    github = models.URLField(verbose_name='博主GitHub主页地址', default='')
    gitee = models.URLField(verbose_name='博主GitEE主页地址', default='')
    recommend_posts = models.ManyToManyField(Post, verbose_name='博主推荐的博文')

    class Meta:
        verbose_name = '博主个人信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


class FriendshipLinks(models.Model):
    name = models.CharField(verbose_name='网站名称', max_length=20)
    url = models.URLField(verbose_name='地址')

    class Meta:
        verbose_name = '友情链接'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name