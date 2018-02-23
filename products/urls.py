from django.conf.urls import re_path
from products import views

urlpatterns = [
    # view : View all Products
    re_path('^view', views.ProductsView.as_view()),
    # change : Add Products
    re_path('^add$', views.EditProductsView.as_view()),
    # 7/change : Delete or Update a Product
    re_path('^(?P<pk>[0-9]+)/change$', views.EditProductsView.as_view()),
    # 7/categories/add : View category options in Product with pk = 7
    re_path('^(?P<pk>[0-9]+)/categories/view$', views.ProductCategoriesView.as_view()),
    # 7/categories/1/add : Add category options cat_pk in Product with pk = 7
    re_path('^(?P<pk>[0-9]+)/categories/(?P<cat_pk>[0-9]+)/add$', views.EditProductCategoriesView.as_view()),
    # 7/categories/add : Delete category option cat_pk in Product with pk = 7
    re_path('^(?P<pk>[0-9]+)/categories/(?P<cat_pk>[0-9]+)/del$', views.EditProductCategoriesView.as_view()),

    # categories/change/ : Add categories
    re_path('^categories/add', views.EditCategoriesView.as_view()),
    # categories/change/7/ : View available, Delete or Update Category options
    re_path('^categories/(?P<pk>[0-9]+)/change', views.EditCategoriesView.as_view()),
    # categories/view : View all categories
    re_path('^categories/view', views.CategoriesView.as_view()),

    # Add a Combo - POST request
    re_path('^combo/add', views.ComboView.as_view()),
    # View all Combos
    re_path('^combo/view', views.ComboView.as_view()),

    re_path('^cart$', views.CartView.as_view()),
    re_path('^order/initiate$', views.InitiateOrderCartView.as_view()),
    re_path('^get/order$', views.GetOrderView.as_view()),

    re_path('^order/initiate/payment$', views.InitiatePaymentView.as_view()),
    re_path('^callback/by/payment/gateway$', views.CallbackByPaymentGatewayView.as_view()),
]
