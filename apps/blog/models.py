import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.
User = get_user_model()
class Tag(models.Model):
    name = models.CharField(verbose_name='标签名称', max_length=20)

    class Meta:
        verbose_name = '博文标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Category(MPTTModel):
    name = models.CharField(verbose_name='类目名称', max_length=20)
    parent = TreeForeignKey('self', related_name='children', db_index=True, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "博文类目"
        verbose_name_plural = verbose_name

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS = (
        ('draft', "草稿"),
        ('published', "已发表")
    )
    title = models.CharField(verbose_name='博文标题', max_length=50, help_text="少于50字符")
    cover = models.ImageField(verbose_name='博文封面', upload_to='blog/blog_cover/%Y/%m', max_length=200, default='blog/blog_cover/default.jpg')
    category = models.ForeignKey(Category, verbose_name="博文类目", on_delete=models.CASCADE) # n ~ 1
    tags = models.ManyToManyField(Tag, verbose_name="博文标签") # m ~ n
    author = models.ForeignKey(User, verbose_name="博文作者", on_delete=models.CASCADE) # n ~ 1
    excerpt = models.CharField(verbose_name="博文摘要", max_length=300)
    content = models.TextField(verbose_name='博文内容')
    status = models.CharField(verbose_name="编辑状态", choices=STATUS, max_length=10, default='draft')
    n_praise = models.PositiveIntegerField(verbose_name="点赞数量", default=0)
    n_comments = models.PositiveIntegerField(verbose_name='评论数量', default=0)
    n_browsers = models.PositiveIntegerField(verbose_name="浏览次数", default=0)
    published_time = models.DateTimeField(verbose_name="发表时间", default=datetime.datetime.now)

    class Meta:
        verbose_name = '博文'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def was_published_recently(self):
        now = datetime.datetime.now()
        return now - datetime.timedelta(days=1) <= self.published_time <= now
    was_published_recently.admin_order_field = 'published_time'
    was_published_recently.boolean = True
    was_published_recently.short_description = '是否是最近发表?'

    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={'pk':self.pk})


class Resources(models.Model):
    post = models.ForeignKey(Post, verbose_name='所属博文', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(verbose_name='资源名称', max_length=50)
    resource = models.FileField(verbose_name='资源文件', max_length=200)
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.datetime.now)

    class Meta:
        verbose_name = '博文资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name