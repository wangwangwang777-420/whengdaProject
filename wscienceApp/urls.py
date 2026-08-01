from django.urls import path
from . import views
app_name = 'wscienceApp'

urlpatterns = [
    path('science/', views.science, name='science'), #科研基地
]
