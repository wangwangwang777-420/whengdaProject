from django.urls import path
from . import views

app_name = 'wnewsApp'

urlpatterns = [
    path('news/<str:newName>/', views.news, name='news'),#咨询中心
    path('newsDetail/<int:id>/', views.newDetail, name='newsDetail'),
    path('search/', views.search, name='search'),
]

