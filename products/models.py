from django.db import models
from django.contrib.postgres.fields import ArrayField
from accounts.models import MyUser


class Products(models.Model):
    """
        This model stores the details of each product
        in the inventory of the Coffee Store.
    """
    name = models.CharField(max_length=150)
    image = models.CharField(max_length=1000)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    avail_quantity = models.IntegerField(default=0)
    desc = models.CharField(max_length=5000)
    rating = models.DecimalField(max_digits=4, decimal_places=2)
    users_rated = models.IntegerField(default=0)
    is_combo = models.BooleanField(default=False)
    combo_product_ids = models.ManyToManyField("self")
    category_ids = ArrayField(models.IntegerField())  # Change to manytomany field after Category table is added.


class Orders(models.Model):
    """
        This model stores all the single orders as well as the orders
        from subscriptions of a user.
    """
    user_id = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    is_subscription = models.BooleanField(default=False)
    customer_order_id = models.BigIntegerField()
    payment_type_choices = (
        ('C', 'Cash on Delivery'),
        ('N', 'Net Banking'),
        ('U', 'UPI'),
        ('D', 'Debit/Credit Cards')
    )
    payment_type = models.CharField(max_length=1, choices=payment_type_choices, default='C')
    payment_status = models.BooleanField(default=False)
    shipping_status = ArrayField(models.CharField(max_length=50))


class CartProducts(models.Model):
    """
        This model stores the products saved by the user in the
        cart.
    """
    user_id = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)





