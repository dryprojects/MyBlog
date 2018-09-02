from django.db import models
from django.utils.timezone import now

# Create your models here.
class Ebook(models.Model):
    title = models.CharField(verbose_name='书名', max_length=100)
    sub_title = models.CharField(verbose_name='副标题', max_length=100, null=True, blank=True)
    cover_url = models.URLField(verbose_name='封面链接')
    author_name = models.CharField(verbose_name='作者名字', max_length=50)
    isbn = models.CharField(verbose_name='ISBN-10', max_length=50)
    published_year = models.CharField(verbose_name='出版年限', max_length=4)
    pages = models.PositiveIntegerField(verbose_name="页数")
    language = models.CharField(verbose_name="书籍语言", max_length=50)
    file_size = models.CharField(verbose_name="电子书大小", max_length=50)
    file_format = models.CharField(verbose_name="电子书格式", max_length=100)
    category = models.CharField(verbose_name="电子书类目", max_length=100)
    description = models.TextField()
    download_links = models.CharField(verbose_name="下载地址", max_length=500)
    url_object_id = models.CharField(verbose_name="url标识", max_length=100, unique=True)
    crawl_time = models.DateTimeField(verbose_name="爬取时间", default=now)

    class Meta:
        verbose_name = "电子书"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.title)