from rest_framework import serializers

from products.models import Products, Categories, CartProducts, Subscriptions, Orders, Combo


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Products
        fields = '__all__'


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('pk', 'period_number', 'period_name', 'terms')


class ComboSerializer(serializers.ModelSerializer):
    class Meta:
        model = Combo
        fields = ('quantity',)


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = ('pk', 'user', 'product', 'quantity', 'start_date', 'category', 'status', 'next_order_date',
                  'last_order_date', 'paid_till')


class CartProductSerializer(serializers.ModelSerializer):
    """
        This is for returning serialized cart products items.
    """
    product = ProductSerializer()
    cost = serializers.FloatField(required=False)

    class Meta:
        model = CartProducts
        exclude = ('user',)


class OrdersSerializers(serializers.ModelSerializer):
    """
        This is for getting the order detials.
    """

    class Meta:
        model = Orders
        fields = '__all__'
