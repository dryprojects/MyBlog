import json
import csv

from django.http import HttpResponse
from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib.contenttypes.models import ContentType
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from django.db.models import F

from blog.models import Post, Tag, Category
from comment.models import Comment

from pure_pagination.mixins import PaginationMixin
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet


# Create your views here.

class PostListView(PaginationMixin, ListView):
    template_name = 'blog/post-list.html'
    model = Post
    ordering = '-published_time'
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status='published', type='post')


class PostDetailView(DetailView):
    template_name = 'blog/post-detail.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = {}
        ct = ContentType.objects.get_for_model(Post)
        cmt_ct = ContentType.objects.get_for_model(Comment)

        context['ct'] = ct.id
        context['cmt_ct'] = cmt_ct.id
        # 可以在这里统计浏览次数
        self.count_browsers()

        return super().get_context_data(**context)

    def count_browsers(self):
        p = self.get_object()
        p.n_browsers = F('n_browsers') + 1
        p.save()


class PostSearchView(PaginationMixin, SearchView):
    template_name = 'search/blog/search-post.html'
    paginate_by = 4


class PostAutoCompleteView(View):
    def get(self, request, *args, **kwargs):
        count = request.GET.get('count', 5)
        q = request.GET.get('q', "")
        try:
            count = int(count)
        except Exception as e:
            return HttpResponse(json.dumps([]), content_type='application/json')
        if q == "":
            return HttpResponse(json.dumps([]), content_type='application/json')
        sqs = SearchQuerySet().autocomplete(title_auto=q)[:int(count)]
        suggestions = [result.object.title for result in sqs]
        return HttpResponse(self.get_sug_context(suggestions), content_type='application/json')

    def get_sug_context(self, suggestions):
        """
        var data = [
        { "value": "1", "label": "one" },
        { "value": "2", "label": "two" },
        { "value": "3", "label": "three" },
        { "value": "4", "label": "four" },
        { "value": "5", "label": "five" },
        { "value": "6", "label": "six" }
    ];
        :param suggestions:
        :return:
        """

        context = []
        for suggest in suggestions:
            context.append({"value": suggest, "label": suggest})
        return json.dumps(context)


class PostArchiveListView(PaginationMixin, ListView):
    template_name = 'blog/post-list.html'
    model = Post
    ordering = '-published_time'
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()
        ar_list = queryset.filter(published_time__year=self.kwargs['year'], published_time__month=self.kwargs['month'])
        return ar_list.filter(status='published', type='post')


class PostTagListView(PaginationMixin, ListView):
    template_name = 'blog/post-list.html'
    model = Post
    ordering = '-published_time'
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = get_object_or_404(Tag, pk=self.kwargs['pk'])
        tag_post_list = queryset.filter(tags=tag)
        return tag_post_list.filter(status='published', type='post')


class PostCategoryListView(PaginationMixin, ListView):
    template_name = 'blog/post-list.html'
    model = Post
    ordering = '-published_time'
    paginate_by = 4

    def get_queryset(self):
        """
        分类前端css只控制到第三级
        所以为了前端便于显示分类不要超过三级， 虽然后端可以无限分类。
        :return:
        """
        queryset = super().get_queryset()
        cg = get_object_or_404(Category, pk=self.kwargs['pk'])
        # 获取该分类的所有子分类
        cg_list = cg.get_descendants(include_self=True)
        queryset = Post.objects.filter(category__in=cg_list, status='published', type='post')
        return queryset


class PostThumbView(SingleObjectMixin, View):
    """
    博文点赞处理
    """
    model = Post

    def post(self, request, pk):
        """
        F表达式
         这种方法没有使用数据库中特定的原始的值，而是当 save() 执行时，让数据库去根据数据库当前的值进行更新操作。
        一旦当前对象被存储时，我们必须重新加载当前对象以获取到当前数据库中最新的值。
        :param request:
        :param pk: 博文主键
        :return:
        """
        self.object = self.get_object()
        self.object.n_praise = F('n_praise') + 1
        self.object.save()

        return HttpResponse(json.dumps({'n_praise': self.get_object().n_praise}))


class BlogAbout(TemplateView):
    template_name = 'blog/about.html'
    extra_context = {
        'title': '博客关于'
    }


class ExportPostView(View):
    def get(self, request, *args, **kwargs):
        """
        服务端博文导出重定向处理：
            查询参数:
                ct  ： 对象内容类型
                ids : 所要导出的对象id 逗号分割
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="MyBlogPosts.csv"'
        writer = csv.writer(response)

        ids = request.GET.get('ids', None)
        queryset = Post.objects.filter(id__in=ids.split(','))
        writer.writerow(['id', 'parent_id', 'title', 'cover', 'category_id',
                         'author_id', 'excerpt', 'content', 'status', 'n_praise',
                         'n_browsers', 'published_time', 'type', 'is_banner',
                         'lft', 'rght', 'tree_id', 'level'
                         ])
        for p in queryset.values_list():
            writer.writerow(p)
        return response
