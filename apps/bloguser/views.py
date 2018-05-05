from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from bloguser import forms


class BlogUserLoginView(auth_views.LoginView):
    template_name = 'bloguser/login.html'


class BlogUserLogutView(auth_views.LogoutView):
    """
    这里不提供模板也行， logoutview会在dispatch时候登出，
    然后检查设置或者查询参数中的重定向url，如果有的话，就直接重定向了，
    从而不会再把请求转发到get,post等方法。
    """


class BlogUserRegisterView(CreateView):
    form_class = forms.BlogUserCreationForm
    template_name = 'bloguser/register.html'