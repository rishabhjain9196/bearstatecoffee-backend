from django.contrib import admin
from products.models import Products, Categories, CartProducts, Subscriptions, MyUser, Orders, Combo


# Register your models here.
admin.site.register(Products)
admin.site.register(CartProducts)
admin.site.register(Categories)
admin.site.register(Subscriptions)
admin.site.register(MyUser)
admin.site.register(Orders)
