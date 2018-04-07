from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, View, TemplateView

from blog.models import Post

from pure_pagination.mixins import PaginationMixin
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