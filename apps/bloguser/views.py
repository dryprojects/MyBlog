from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin

from bloguser import forms


class BlogUserLoginView(auth_views.LoginView):
    template_name = 'bloguser/login.html'


