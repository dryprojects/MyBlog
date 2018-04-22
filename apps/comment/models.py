import datetime

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.
User = get_user_model()

class Comment(MPTTModel):
    parent = TreeForeignKey('self', verbose_name='父级评论', on_delete=models.CASCADE, related_name='children', db_index=True, null=True, blank=True, default=1)
    content = models.TextField(verbose_name='评论内容')
    author = models.ForeignKey(User, verbose_name='评论者', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, verbose_name='评论附加对象的ct类型', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(verbose_name='评论附加对象id')
    content_object = GenericForeignKey('content_type', 'object_id') #被评论附加的对象
    published_time = models.DateTimeField(verbose_name='评论时间', default=datetime.datetime.now)
    n_like = models.PositiveIntegerField(verbose_name='评论喜欢数', default=0)
    n_dislike = models.PositiveIntegerField(verbose_name='评论讨厌数', default=0)
    is_spam = models.BooleanField(verbose_name='是否是评论垃圾', default=False)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        app_label = 'comment'

    class MPTTMeta:
        order_insertion_by = ['published_time']

    def __str__(self):
        return "{0} ({1})".format(self.content[:20] if self.content else "", self.id)

    @property
    def n_sub_comment(self):
        """
        该评论的子评论个数
        :return:
        """
        return 0

    def was_published_recently(self):
        now = datetime.datetime.now()
        return now - datetime.timedelta(days=1) <= self.published_time <= now

    was_published_recently.admin_order_field = 'published_time'
    was_published_recently.boolean = True
    was_published_recently.short_description = '是否是最近发表?'

    # def content_object_name(self):
    #     model = self.content_type.model_class()
    #     object = model.objects.filter(pk=self.object_id)[0]
    #     return str(object)
    # content_object_name.short_description = '评论附加对象'

"""
查询某一篇博客的所有评论
post = Post.objects.all().get(..)
post_ct = ContentType.object.get_for_model(Post)
Comment.object.filter(content_type__pk=post_ct.id, object_id=post.id)
"""