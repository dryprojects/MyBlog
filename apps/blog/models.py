import datetime
import hashlib

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from django.db import transaction

from mptt.models import MPTTModel, TreeForeignKey
from mptt.utils import previous_current_next

from comment.models import Comment

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


class Post(MPTTModel):
    STATUS = (
        ('draft', "草稿"),
        ('published', "已发表")
    )
    TYPES = (
        ('post', '博文'),
        ('notification', '公告')
    )
    parent = TreeForeignKey('self', verbose_name='上一篇博文', related_name='children', db_index=True, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(verbose_name='博文标题', max_length=50, help_text="少于50字符")
    cover = models.ImageField(verbose_name='博文封面', upload_to='blog/blog_cover/%Y/%m', max_length=200, default='blog/blog_cover/default.jpg')
    cover_url = models.URLField(verbose_name="博文封面url", default="")
    category = models.ForeignKey(Category, verbose_name="博文类目", on_delete=models.CASCADE) # n ~ 1
    tags = models.ManyToManyField(Tag, verbose_name="博文标签") # m ~ n
    author = models.ForeignKey(User, verbose_name="博文作者", on_delete=models.CASCADE, blank=True, null=True) # n ~ 1
    excerpt = models.TextField(verbose_name="博文摘要", blank=True)
    content = models.TextField(verbose_name='博文内容')
    status = models.CharField(verbose_name="编辑状态", choices=STATUS, max_length=10, default='draft')
    n_praise = models.PositiveIntegerField(verbose_name="点赞数量", default=0)
    n_browsers = models.PositiveIntegerField(verbose_name="浏览次数", default=0)
    published_time = models.DateTimeField(verbose_name="发表时间", default=datetime.datetime.now)
    comments = GenericRelation(Comment, related_query_name='post')
    type = models.CharField(verbose_name="博文类型", choices=TYPES, max_length=13, default='post')
    is_banner = models.BooleanField(verbose_name='是否是轮播图', default=False)
    origin_post_url = models.URLField(verbose_name='原博文URL链接', default="", null=True, blank=True)
    origin_post_from = models.CharField(verbose_name="原博文出处名称", max_length=255, default="", null=True, blank=True)
    url_object_id = models.CharField(verbose_name="源博文唯一标识", unique=True, max_length=255, null=True, blank=True, help_text="不写默认为博文url摘要")

    class Meta:
        verbose_name = '博文'
        verbose_name_plural = verbose_name

    class MPTTMeta:
        order_insertion_by = ['title']

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

    @property
    def n_comments(self):
        """
        获取该博文的所有评论个数
        :return:
        """
        root_count = 0
        sub_count = 0

        with transaction.atomic():
            #这里的comments都是content_type为Post的评论，（根评论）
            for comment in self.comments.all():
                if comment:
                    root_count += 1
                    sub_count += comment.n_sub_comment

        return root_count + sub_count

    @property
    def n_comment_users(self):
        """
        该博文评论用户的参与人数
        :return:
        """
        user_set = set()
        with transaction.atomic():
            for root_comment in self.comments.all():
                if root_comment:
                    for sub_comment in root_comment.get_descendants(include_self=True).all():
                        user_set.add(sub_comment.author.username)

        return len(user_set)

    @property
    def prev_this_next(self):
        """
        返回上一篇博文， 当前博文， 下一篇博文的元组
        如果上一篇或者下一篇不存在， 元组对应位置返回 None
        :return: tuple
        """
        queryset = self.get_root().get_descendants(include_self=True)
        for t in previous_current_next(queryset):
            if t[1] == self:
                return t

    @property
    def prev(self):
        """
        返回上一篇博文
        :return:
        """
        return self.prev_this_next[0]

    @property
    def next(self):
        """
        返回下一篇博文
        :return:
        """
        return self.prev_this_next[2]

    def save(self, *args, **kwargs):
        """
        如果有本地封面则cover_url为本地封面， 否则使用爬虫获取的封面.
        如果博文category为None,则自动添加到默认分类其他
        用博文的文的url生成唯一博文索引
        :param args:
        :param kwargs:
        :return:
        """
        super(Post, self).save()
        if self.cover.url is not None:
            self.cover_url = self.cover.url

        if self.category is None:
            self.category = Category(name="其他")

        m = hashlib.md5()
        m.update(self.get_absolute_url().encode('utf-8'))
        self.url_object_id = m.hexdigest()
        super(Post, self).save()


class Resources(models.Model):
    post = models.ForeignKey(Post, verbose_name='所属博文', on_delete=models.CASCADE, blank=True, null=True, related_name='resources')
    name = models.CharField(verbose_name='资源名称', max_length=50)
    resource = models.FileField(verbose_name='资源文件', max_length=200, upload_to='blog/resources/%Y/%m/')
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.datetime.now)

    class Meta:
        verbose_name = '博文资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name