import json

from django.contrib.auth import views as auth_views
from django.contrib.auth.tokens import default_token_generator
from django.views.generic.edit import FormView, View, FormMixin
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.http import Http404, HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, resolve_url

from pure_pagination.mixins import PaginationMixin

from bloguser import forms
from bloguser import mixins
from bloguser.models import UserProfile
from oper.models import Notification
from oper.tasks import get_n_unread, mark_as_read


class BlogUserLoginView(auth_views.LoginView):
    template_name = 'bloguser/login.html'


class BlogUserLogutView(auth_views.LogoutView):
    """
    这里不提供模板也行， logoutview会在dispatch时候登出，
    然后检查设置或者查询参数中的重定向url，如果有的话，就直接重定向了，
    从而不会再把请求转发到get,post等方法。
    """


class BlogUserRegisterView(mixins.RedirectMixin, FormView):
    """
    用户注册，帐号需要进行邮箱验证后才可登陆
    """
    form_class = forms.BlogUserCreationForm
    template_name = 'bloguser/register.html'
    subject_template_name = 'bloguser/register_active_subject.txt'
    email_template_name = 'bloguser/register_active_email.html'

    def form_valid(self, form):
        try:
            user = form.save(commit=True, subject_template_name=self.subject_template_name,
                             email_template_name=self.email_template_name, request=self.request)
        except ValidationError as error:
            form.add_error('email', error)
            return self.form_invalid(form)

        return super().form_valid(form)


class BlogUserActiveConfirmView(View):
    """
    用户邮箱激活验证
    """

    def get(self, request, uidb64, token, active_done_redirect=None):
        if active_done_redirect is None:
            active_done_redirect = reverse('bloguser:bloguser-login')
        else:
            active_done_redirect = resolve_url(active_done_redirect)

        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserProfile.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            # 通知用户激活成功
            content = '你的邮箱：%s, 验证成功！感谢你对本站的支持！！' % user.email
            user.notify_user(content)

            return redirect(active_done_redirect)
        else:
            raise Http404("无效邮箱验证请求")


class BlogUserAccountView(LoginRequiredMixin, PaginationMixin, mixins.RedirectMixin, FormMixin, ListView):
    """
    用户个人中心
        个人信息
        通知
    """
    template_name = 'bloguser/usercenter.html'
    form_class = forms.BlogUserChangeForm
    queryset = Notification.objects.all()
    paginate_by = 15
    ordering = '-published_time'

    def post(self, request):
        """
        更新用户个人信息
        :param request:
        :return:
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_queryset(self):
        """
        获取用户的相关通知
        :return:
        """
        queryset = super().get_queryset()

        return queryset.filter(user=self.request.user)

    def form_valid(self, form):
        """
        更新用户信息
        :param form:
        :return:
        """
        form.save()

        return super().form_valid(form)

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': self.request.user
        })

        return kwargs


class BlogUserDetailView(DetailView):
    model = Notification
    template_name = 'bloguser/usercenter-noti-detail.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse(json.dumps({'status':'success'}), status=204, content_type="application/json")

    def get_context_data(self, **kwargs):
        """将用户通知标记为已读"""
        if not self.object.has_read:
            # 更新缓存
            mark_as_read(self.request.user.pk, self.kwargs.get('pk'))

        context = super().get_context_data(**kwargs)
        return context


class BlogUserPasswordResetView(auth_views.PasswordResetView):
    """
    重置密码
    """
    template_name = 'bloguser/password_reset_form.html'
    email_template_name = 'bloguser/password_reset_email.html'
    success_url = reverse_lazy('bloguser:bloguser-password-reset-done')
    form_class = forms.BlogUserPasswordResetForm


class BlogUserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'bloguser/password_reset_done.html'


class BlogUserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'bloguser/password_reset_confirm.html'
    success_url = reverse_lazy('bloguser:bloguser-password-reset-complete')


class BlogUserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'bloguser/password_reset_complete.html'
