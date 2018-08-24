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
from django.contrib.sitemaps import views as sitemap_views

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.conf.urls.static import static

import social_django.urls
from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view

from blog.admin import USE_ADMIN_SITE, ADD_PASSWORD_FORGET

if not USE_ADMIN_SITE:
    from blog.admin import admin_site

from blog.sitemaps import BlogSitemap

if not settings.API_MODE:
    urlpatterns = [
        path('', include('blog.urls', namespace='blog')),
    ]
else:
    urlpatterns = [
        path('blog/', include('blog.urls', namespace='blog')),
        path('auth/', include('djoser.urls')),
        path('auth/', include('djoser.social.urls')),
        path('auth/', include('djoser.urls.authtoken')),
        path('auth/', include('djoser.urls.jwt')),
        path('account/', include('bloguser.urls', namespace='bloguser')),
        path('trade/', include('trade.urls')),
        path('trade/', include('trade.alipay.urls'))
    ]

urlpatterns.extend([
    path('comment/', include('comment.urls', namespace='comment')),
    path('kindeditor/', include('kindeditor.urls', namespace='kindeditor')),
    path('mdeditor/', include('mdeditor.urls', namespace='mdeditor')),
    path('social/', include('social_django.urls', namespace='social')),
    path('captcha/', include('captcha.urls')),
])

if settings.DEBUG:
    urlpatterns.extend([
        path('docs/', include_docs_urls(title='MyBlog Api Docs', public=False)),
        #path('docs/', get_swagger_view(title='MyBlog Api Docs')),
        path('api-auth/', include('rest_framework.urls')),
    ])

sitemaps = {
    'blog': BlogSitemap
}

urlpatterns += [
    path('sitemap.xml', sitemap_views.index, {'sitemaps': sitemaps}),
    path('sitemap-<section>.xml', sitemap_views.sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
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

# see more https://docs.djangoproject.com/en/2.0/topics/http/views/
if not settings.DEBUG:
    handler404 = 'django.views.defaults.page_not_found'
    handler500 = 'django.views.defaults.server_error' if not settings.API_MODE else 'rest_framework.exceptions.server_error'
    handler403 = 'django.views.defaults.permission_denied'
    handler400 = 'django.views.defaults.bad_request' if not settings.API_MODE else 'rest_framework.exceptions.bad_request'
