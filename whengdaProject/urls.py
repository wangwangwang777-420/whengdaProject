"""whengdaProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from django.conf.urls import include
from whomeApp.views import home
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), #管理员
    path('',home,name='home'), #首页
    path('waboutApp/', include('waboutApp.urls')), #公司简介
    path('wcontactApp/', include('wcontactApp.urls')), #人才招聘
    path('wnewsApp/', include('wnewsApp.urls')), #咨询中心
    path('wproductApp/', include('wproductApp.urls')), #产品中心
    path('wscienceApp/', include('wscienceApp.urls')), #科研基地
    path('wserviceApp/', include('wserviceApp.urls')), #服务支持
    path('ueditor/', include('DjangoUeditor.urls')),
    path('search/', include('haystack.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)