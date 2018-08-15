from django.contrib import admin
from django.utils.html import format_html

from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter

from comment.models import Comment


# Register your models here.
@admin.register(Comment)
class CommentModelAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'get_comment','parent', 'author', 'content_object', 'published_time', 'was_published_recently']
    list_display_links = ['get_comment']
    list_filter = (
        ('parent', TreeRelatedFieldListFilter),
    )
    autocomplete_fields = ['author', 'parent']
    search_fields = ['id']
    fieldsets = [
        ('评论信息', {
            "fields": [('content', 'content_type', 'object_id'), ('author', 'published_time')],
            'classes': ('extrapretty')
        }),
        ('评论元数据', {
            "fields": ['parent', ('n_like', 'n_dislike', 'is_spam')],
            'classes': ('extrapretty')
        })
    ]
    readonly_fields = ['n_like', 'n_dislike']

    def content_object(self, instance):
        if hasattr(instance.content_object, 'get_absolute_url'):
            return format_html("<a href='{}'>{}</a>", instance.content_object.get_absolute_url(), instance.content_object)
        return instance.content_object
    content_object.short_description = '被评论对象'

    def get_comment(self, instance):
        return format_html(
            '<div style="text-indent:{}px">{}</div>',
            instance._mpttfield('level') * self.mptt_level_indent,
            instance,  # Or whatever you want to put here
        )

    get_comment.short_description = "评论"