from django.contrib import admin
from django.urls import path
from django.conf.urls import include, re_path
from .serializers import ProductSerializer
from products import views

urlpatterns = [
    path('view/', views.ProductsView.as_view()),
    re_path('change/(?P<pk>[0-9]+)/', views.EditProducts.as_view())
]
