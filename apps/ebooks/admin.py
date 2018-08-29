import os

from django.contrib import admin
from django.utils.html import format_html
from django.db import models

# Register your models here.
from ebooks.models import Ebook
from mdeditor.widgets import MdTextWidget


@admin.register(Ebook)
class EbookModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_cover', 'isbn', 'file_size', 'file_format', 'download_link1', 'download_link2']
    formfield_overrides = {
        models.TextField: {
            'widget': MdTextWidget
        }
    }

    fieldsets = [
        ('基本信息',
         {"fields": [('title', 'sub_title', 'category'), ('author_name', 'published_year'), 'description'], 'classes': ('wide', 'extrapretty')}),
        ('附加信息', {"fields": [('cover_url', 'isbn'), ('pages', 'language', 'file_size', 'file_format'), ('url_object_id', 'crawl_time'), 'download_link1', 'download_link2',], "classes": ('wide', 'extrapretty')}),
    ]

    readonly_fields = ('isbn', 'url_object_id', 'file_size', 'file_format', 'download_link1', 'download_link2', 'author_name', 'pages', 'language', 'crawl_time')
    list_per_page = 10
    list_filter = ('title', 'isbn', 'author_name')
    search_fields = ('title',)

    def get_cover(self, obj):
        return format_html("<img src='{}' alt='' width='350' height='499'/>", obj.cover_url)

    def download_link1(self, obj):
        return self.get_download_link(obj)

    def download_link2(self, obj):
        return self.get_download_link(obj, 2)

    def get_download_link(self, obj, index=1):
        download_links = obj.download_links.split('|')
        if len(download_links) >= index:
            ext = os.path.splitext(download_links[index-1])[1]
            return format_html("<a href='{}'>{}格式下载</a>", download_links[index-1], ext)
        return ""

    download_link1.short_description = "下载地址1"
    download_link2.short_description = "下载地址2"
    get_cover.short_description = '封面'