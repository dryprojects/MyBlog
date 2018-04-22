"""MyBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.contrib.auth import views as auth_views

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.conf.urls.static import static

from blog.admin import USE_ADMIN_SITE, ADD_PASSWORD_FORGET
if not USE_ADMIN_SITE:
    from blog.admin import admin_site

import social_django.urls
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('comment/', include('comment.urls', namespace='comment')),
    path('social/', include('social_django.urls', namespace='social')),
    path('api-auth/', include('rest_framework.urls')),
    path('docs/', include_docs_urls(title='MyBlog Api Docs', public=False))
]

if not USE_ADMIN_SITE:
    urlpatterns += [path('admin/', admin_site.urls)]
else:
    urlpatterns += [path('admin/', admin.site.urls)]

if ADD_PASSWORD_FORGET:
    urlpatterns += [
        path(
            'admin/password_reset/',
            auth_views.PasswordResetView.as_view(),
            name='admin_password_reset',
        ),
        path(
            'admin/password_reset/done/',
            auth_views.PasswordResetDoneView.as_view(),
            name='password_reset_done',
        ),
        path(
            'reset/<uidb64>/<token>/',
            auth_views.PasswordResetConfirmView.as_view(),
            name='password_reset_confirm',
        ),
        path(
            'reset/done/',
            auth_views.PasswordResetCompleteView.as_view(),
            name='password_reset_complete',
        ),
    ]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)