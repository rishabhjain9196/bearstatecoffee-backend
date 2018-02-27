from django.test import TestCase

from rest_framework.test import force_authenticate, APIRequestFactory

from accounts.models import MyUser
from products.models import Products, CartProducts
from accounts.views import UserDetailsView
from products.views import CartView
# Create your tests here.


class CartProductsTests(TestCase):
    """
        This will test the apis.
    """
    @classmethod
    def setUpTestData(cls):
        cls.total_products = 30
        cls.total_admin_user = 10
        cls.total_user = 10

        for counter in range(cls.total_products):
            Products.objects.create(name='Product %s' % counter, image='Random URL', cost=50.00, avail_quantity=100,
                                    desc='Sample Desc')

        for counter in range(cls.total_admin_user):
            data = {
                'email': 'nipun.garg%s@kuliza.com' % counter,
                'password': 'nipun%s' % counter,
                'first_name': 'Nipun',
                'last_name': 'Garg',
                'phone_number': '+918860447251',
                'is_verified': True
            }
            MyUser.objects.create_superuser(**data)

        for counter in range(cls.total_user):
            data = {
                'email': 'nipun.garg1%s@kuliza.com' % counter,
                'password': 'nipun1%s' % counter,
                'first_name': 'Nipun',
                'last_name': 'Garg',
                'phone_number': '+918860447251',
                'is_verified': True
            }
            MyUser.objects.create_user(**data)

    def test_authentication_check(self):
        print(Products.objects.values(), '\n\n\n')
        print(MyUser.objects.values(), '\n\n\n')

        factory = APIRequestFactory()
        user = MyUser.objects.get(pk=1)
        view = UserDetailsView.as_view()

        request = factory.get('/accounts/profile/')
        force_authenticate(request, user=user)

        response = view(request)
        self.assertEqual(response.status_code, 200, 'Unable to authenticate user.')

    def test_cart_view_post(self):
        # Added to cart
        user = MyUser.objects.get(pk=1+self.total_admin_user)
        factory = APIRequestFactory()
        view = CartView.as_view()
        request = factory.post('/products/cart', {
            'product_id': 1,
            'quantity': 30
        })
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code, 200, 'Adding to cart failed.')

        # Add Extra Quantity
        request = factory.post('/products/cart', {
            'product_id': 1,
            'quantity': 80
        })

        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 400, 'Quantity Check Failed.')

        # Cart Products Validation check

        cart_products = CartProducts.objects.filter(user=user, is_active=True)
        print(cart_products)

        request = factory.delete('/products/cart', {
            'quantity': cart_products[0].quantity
        })
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code, 400, 'Cart Product id validation failed.')

        request = factory.delete('/products/cart', {
            'cart_product_id': cart_products[0].id
        })
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code, 400, 'Quantity Validation failed')

        # Cart product successful removal

        request = factory.delete('/products/cart', {
            'cart_product_id': cart_products[0].id,
            'quantity': cart_products[0].quantity
        })
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200, 'Remove from cart failed')
