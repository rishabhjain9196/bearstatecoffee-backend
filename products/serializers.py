from rest_framework import serializers
from products.models import Products, Categories, CartProducts, Subscriptions, Orders, Combo


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Products
        fields = ('pk', 'name', 'image', 'cost', 'avail_quantity', 'desc', 'rating', 'users_rated', 'is_combo',
                  'is_delete')


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('pk', 'period_number', 'period_name', 'terms')


class ComboSerializer(serializers.ModelSerializer):
    class Meta:
        model = Combo
        fields = ('quantity',)


class CartProductSerializer(serializers.ModelSerializer):
    """
        This is for returning serialized cart products items.
    """
    class Meta:
        model = CartProducts
        fields = '__all__'
