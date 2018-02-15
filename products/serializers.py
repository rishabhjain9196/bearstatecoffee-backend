from rest_framework import serializers
from products.models import Products, Categories, CartProducts, Subscriptions, Orders


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ('pk', 'name', 'image', 'cost', 'avail_quantity', 'desc', 'rating', 'users_rated', 'is_combo',
                  'is_delete')
