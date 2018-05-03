import json

from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, View, TemplateView
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.shortcuts import get_object_or_404

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
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status='published')


class PostDetailView(DetailView):
    template_name = 'blog/post-detail.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = {}
        ct = ContentType.objects.get_for_model(Post)
        cmt_ct = ContentType.objects.get_for_model(Comment)

        context['ct'] = ct.id
        context['cmt_ct'] = cmt_ct.id
        #可以在这里统计浏览次数
        self.count_browsers()

        return super().get_context_data(**context)

    def count_browsers(self):
        p = self.get_object()
        p.n_browsers += 1
        p.save()


class PostSearchView(PaginationMixin, SearchView):
    template_name = 'search/blog/search-post.html'
    paginate_by = 3


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
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        ar_list = queryset.filter(published_time__year=self.kwargs['year'], published_time__month=self.kwargs['month'])
        return ar_list.filter(status='published')


class PostTagListView(PaginationMixin, ListView):
    template_name = 'blog/post-list.html'
    model = Post
    ordering = '-published_time'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = get_object_or_404(Tag, pk=self.kwargs['pk'])
        tag_post_list = queryset.filter(tags=tag)
        return tag_post_list.filter(status='published')


class PostCategoryListView(PaginationMixin, ListView):
    template_name = 'blog/post-list.html'
    model = Post
    ordering = '-published_time'
    paginate_by = 3

    def get_queryset(self):
        """
        分类前端css只控制到第三级
        所以为了前端便于显示分类不要超过三级， 虽然后端可以无限分类。
        :return:
        """
        queryset = super().get_queryset()
        cg = get_object_or_404(Category, pk=self.kwargs['pk'])
        #获取该分类的所有子分类
        cg_list = cg.get_descendants(include_self=True)
        queryset = Post.objects.filter(category__in=cg_list, status='published')
        return queryset