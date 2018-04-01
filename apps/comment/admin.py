from django.contrib import admin
from comment.models import Comment

# Register your models here.
@admin.register(Comment)
class CommentModelAdmin(admin.ModelAdmin):
    autocomplete_fields = ['author']
    fieldsets = [
        ('评论信息',{
            "fields":[('content', 'content_type', 'content_object_name'), ('author', 'published_time')],
            'classes': ('extrapretty')
        }),
    ]
    readonly_fields = ['object_id', 'content_object_name', 'content_type']
    list_display = ['title', 'author', 'content_type', 'content_object_name', 'published_time']