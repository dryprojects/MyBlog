from django.contrib import admin
from blog.models import Post, Category, Tag, Resources

# Register your models here.
class PostTagRelationShipInline(admin.TabularInline):
    model = Post.tags.rel.through
    extra = 1


class ResourcesInline(admin.TabularInline):
    model = Resources
    extra = 1


@admin.register(Post)
class PostModalAdmin(admin.ModelAdmin):
    """
    see detail:
        https://docs.djangoproject.com/en/2.0/intro/tutorial07/
    """
    fieldsets = [
        ('博文基本信息',  {"fields":[('title', 'category', 'author'), 'excerpt', 'content'], 'classes': ('wide', 'extrapretty')}),
        ('博文附加信息',  {"fields":['cover', ('n_praise', 'n_comments', 'n_browsers')], "classes":['collapse']}),
        ('发表时间',      {'fields':['published_time']})
    ]
    inlines = [PostTagRelationShipInline, ResourcesInline]
    exclude = ['tags']
    readonly_fields = ['n_praise', 'n_comments', 'n_browsers']
    list_display = ['title', 'category', 'author', 'cover', 'published_time', 'was_published_recently']
    list_filter = ['published_time']
    search_fields = ['title']
    date_hierarchy = 'published_time'


@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    fields = ['name']

@admin.register(Tag)
class TagModelAdmin(admin.ModelAdmin):
    fields = ['name']