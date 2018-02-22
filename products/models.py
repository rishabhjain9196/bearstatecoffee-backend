from django.db import models
from django.contrib.postgres.fields import ArrayField
from accounts.models import MyUser


class Categories(models.Model):
    """
        This links the products to their specific available periodicity for subscription
        period_number is an integer representation (id) for the corresponding period_name.
    """
    period_number = models.IntegerField()
    period_name = models.CharField(max_length=100)
    terms = models.CharField(max_length=5000)
    is_delete = models.BooleanField(default=False)


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
    rating = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    users_rated = models.IntegerField(default=0)
    is_combo = models.BooleanField(default=False)
    combo_product_ids = models.ManyToManyField("self", through='Combo', symmetrical=False)
    category_ids = models.ManyToManyField("Categories")
    is_delete = models.BooleanField(default=False)


class Combo(models.Model):
    """
        This model is to add extra field - quantity to the many to many relationship
        of combos with products.
    """
    combo = models.ForeignKey(Products, related_name="combo_combo_id", on_delete=models.CASCADE)
    product = models.ForeignKey(Products, related_name="quantity", on_delete=models.CASCADE)
    quantity = models.IntegerField()


class CartProducts(models.Model):
    """
        This model stores the products saved by the user in the
        cart.
    """
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)


class Subscriptions(models.Model):
    """
        This model stores the subscriptions of the all the users.
    """
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    start_date = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    status_choices = (
        ('A', 'ACTIVE'),
        ('P', 'PAUSED'),
        ('C',  'CANCELLED'),
        ('F', 'FINISHED'),
        ('I', 'INACTIVE')
    )
    status = models.CharField(max_length=1, choices=status_choices, default='I')
    next_order_date = models.DateTimeField(blank=True, null=True)
    last_order_date = models.DateTimeField(blank=True, null=True)
    paid_till = models.DateTimeField(blank=True, null=True)


class Orders(models.Model):
    """
        This model stores all the single orders as well as the orders
        from subscriptions of a user.
    """
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    is_subscription = models.BooleanField(default=False)
    customer_order_id = models.BigIntegerField()
    subscription = models.ForeignKey(Subscriptions, on_delete=models.CASCADE)
    payment_type_choices = (
        ('C', 'CASH ON DELIVERY'),
        ('N', 'NET BANKING'),
        ('U', 'UPI'),
        ('D', 'DEBIT/CREDIT CARDS')
    )
    payment_type = models.CharField(max_length=1, choices=payment_type_choices, default='C')
    payment_status = models.BooleanField(default=False)
    shipping_status = ArrayField(models.CharField(max_length=50))
