import json

from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, View, TemplateView
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from blog.models import Post

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

        context['ct'] = ct.id
        context['comment_url'] = reverse('comment:comment-list')
        context['comment_like_url'] = reverse('comment:comment-like')

        return super().get_context_data(**context)


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
