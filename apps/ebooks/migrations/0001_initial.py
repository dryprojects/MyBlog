# Generated by Django 2.0.3 on 2018-08-30 01:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ebook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='书名')),
                ('sub_title', models.CharField(blank=True, max_length=100, null=True, verbose_name='副标题')),
                ('cover_url', models.URLField(verbose_name='封面链接')),
                ('author_name', models.CharField(max_length=50, verbose_name='作者名字')),
                ('isbn', models.CharField(max_length=50, verbose_name='ISBN-10')),
                ('published_year', models.CharField(max_length=4, verbose_name='出版年限')),
                ('pages', models.PositiveIntegerField(verbose_name='页数')),
                ('language', models.CharField(max_length=50, verbose_name='书籍语言')),
                ('file_size', models.CharField(max_length=50, verbose_name='电子书大小')),
                ('file_format', models.CharField(max_length=100, verbose_name='电子书格式')),
                ('category', models.CharField(max_length=100, verbose_name='电子书类目')),
                ('description', models.TextField()),
                ('download_links', models.CharField(max_length=500, verbose_name='下载地址')),
                ('url_object_id', models.CharField(max_length=100, unique=True, verbose_name='url标识')),
                ('crawl_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='爬取时间')),
            ],
            options={
                'verbose_name': '电子书',
                'verbose_name_plural': '电子书',
            },
        ),
    ]