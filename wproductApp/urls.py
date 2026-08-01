from django.urls import path
from . import views
app_name = 'wproductApp'

urlpatterns = [
    path('products/<str:productName>/',views.products,name='products'),
    path('productDetail/<int:id>/',views.productDetail, name='productDetail'),
]
