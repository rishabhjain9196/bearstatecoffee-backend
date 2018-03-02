from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from accounts.models import MyUser
from accounts.views import UserDetailsView
from products.views import CartView, InitiateOrderCartView, InitiatePaymentView, CallbackByPaymentGatewayView, \
    CancelOrderView, ViewAllOrders, EditProductsView, EditCategoriesView
from products.models import Products, Categories, CartProducts
# Create your tests here.


class ProductsViewTest(TestCase):
    """
    Test Case Class for testing Products APIs
    """

    factory = APIRequestFactory()
    admin_user = MyUser.objects.get(is_superuser=True)

    @classmethod
    def setUpTestData(cls):
        total_products = 30
        total_users = 50
        # Populating Products
        for counter in range(total_products):
            Products.objects.create(pk=counter, name='Product %s' % counter, image='Random URL', cost=50.00, avail_quantity=100,
                                    desc='Sample Desc')

        # Creating Superuser
        MyUser.objects.create_superuser(email='rishabh.jain@kuliza.com', password='qwerty',
                                        is_verified=True, phone_number='8744985115', first_name='Rishabh',
                                        last_name='Jain')
        # Populating Categories
        Categories.objects.create(pk=2, period_number=1, period_name='Daily', terms='Sample terms')
        Categories.objects.create(pk=3, period_number=2, period_name='Daily', terms='Sample terms 2')
        Categories.objects.create(pk=4, period_number=2, period_name='Daily', terms='Sample terms 2')

        # Populating users
        for counter in range(total_users):
            data = {
                'email': 'rishabh.jain.%s@kuliza.com' % counter,
                'password': 'qwerty',
                'first_name': 'Rishabh',
                'last_name': 'Jain',
                'phone_number': '+918744985115',
                'is_verified': True
            }
            MyUser.objects.create_user(**data)

    def test_view_all_products(self):
        url = '/products/view'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_add_product(self):
        url = '/products/add'
        view = EditProductsView.as_view()

        payload = {
            'image': 'https://goo.gl/aYwphE',
            'cost': '50.00',
            'avail_quantity': 100,
            'desc': 'Test Description!'
        }

        request = self.factory.post(url, data=payload)
        force_authenticate(request, user=self.admin_user)
        response = view(request)
        self.assertEqual(response.status_code, 400)

        payload['name'] = 'test'
        request = self.factory.post(url, data=payload)
        force_authenticate(request, user=self.admin_user)
        response = view(request)
        self.assertEqual(response.status_code, 201)

    def test_update_product(self):
        url = '/products/1/change'
        view = EditProductsView.as_view()
        payload = {
            'image': 'Updated image url'
        }
        # Primary Key Exists
        request = self.factory.patch(url, data=payload)
        force_authenticate(request, user=self.admin_user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)

        # Primary Key Does not Exists
        url = '/products/100/change'
        request = self.factory.patch(url, data=payload)
        force_authenticate(request, user=self.admin_user)
        response = view(request, pk=100)
        self.assertEqual(response.status_code, 404)

    def test_delete_product(self):
        url = '/products/2/change'
        view = EditProductsView.as_view()

        # Primary Key Exists
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin_user)
        response = view(request, pk=2)
        self.assertEqual(response.status_code, 200)

        # Primary Key Does not Exists
        url = '/products/200/change'
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin_user)
        response = view(request, pk=200)
        self.assertEqual(response.status_code, 400)

    def test_view_all_categories(self):
        url = '/products/categories/view'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_add_category(self):
        url = '/products/categories/add'
        view = EditCategoriesView.as_view()

        payload = {
                "period_number": "1",
                "period_name": "Daily",
                "terms": "Sample Terms"
        }

        request = self.factory.post(url, data=payload)
        force_authenticate(request, user=self.admin_user)
        response = view(request)
        self.assertEqual(response.status_code, 201)

        payload = {
            "period_number": "1"
        }

        request = self.factory.post(url, data=payload)
        force_authenticate(request, user=self.admin_user)
        response = view(request)
        self.assertEqual(response.status_code, 400)

    def test_update_category(self):
        url = '/products/categories/2/change'
        view = EditCategoriesView.as_view()
        payload = {
            'period_number': '2',
            'period_name': 'Day',
            'terms': 'Sample Terms Updated'
        }
        # Primary Key Exists
        request = self.factory.patch(url, data=payload)
        force_authenticate(request, user=self.admin_user)
        response = view(request, pk=2)
        self.assertEqual(response.status_code, 200)

        # Primary Key Does not Exists
        url = '/products/categories/100/change'
        request = self.factory.patch(url, data=payload)
        force_authenticate(request, user=self.admin_user)
        response = view(request, pk=100)
        self.assertEqual(response.status_code, 404)

    def test_delete_category(self):
        url = '/products/categories/3/change'
        view = EditCategoriesView.as_view()

        # Primary Key Exists
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin_user)
        response = view(request, pk=3)
        self.assertEqual(response.status_code, 200)

        # Primary Key Does not Exists
        url = '/products/categories/200/change'
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin_user)
        response = view(request, pk=200)
        self.assertEqual(response.status_code, 404)


class CartProductsTests(TestCase):
    """
        This will test the APIs.
    """

    @classmethod
    def setUpTestData(cls):
        cls.total_products = 30
        cls.total_admin_user = 10
        cls.total_user = 10
        cls.factory = APIRequestFactory()

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

        cls.user = MyUser.objects.get(pk=1+cls.total_admin_user)
        cls.admin_user = MyUser.objects.get(pk=1)
        cls.product = Products.objects.get(pk=1)
        cls.cart_products_user = CartProducts.objects.create(user=cls.user, product=cls.product, quantity=10)
        cls.cart_products_admin_user = CartProducts.objects.create(user=cls.user, product=cls.product, quantity=10)

    def test_authentication_check(self):
        user = MyUser.objects.get(pk=1)
        view = UserDetailsView.as_view()

        request = self.factory.get('/accounts/profile/')
        force_authenticate(request, user=user)

        response = view(request)
        self.assertEqual(response.status_code, 200, 'Unable to authenticate user.')

    def test_cart_view_post(self):
        # Added to cart
        user = MyUser.objects.get(pk=1+self.total_admin_user)
        view = CartView.as_view()
        request = self.factory.post('/products/cart', {
            'product_id': 1,
            'quantity': 30
        })
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code, 200, 'Adding to cart failed.')

        # Add Extra Quantity
        request = self.factory.post('/products/cart', {
            'product_id': 1,
            'quantity': 80
        })

        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 400, 'Quantity Check Failed.')

        # Get Cart
        request = self.factory.get('/products/cart')

        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200, 'Get Cart Failed.')

        # Cart Products Validation check
        cart_products = CartProducts.objects.filter(user=user, is_active=True)

        request = self.factory.delete('/products/cart', {
            'quantity': cart_products[0].quantity
        })
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code, 400, 'Cart Product id validation failed.')

        request = self.factory.delete('/products/cart', {
            'cart_product_id': cart_products[0].id
        })
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code, 400, 'Quantity Validation failed')

        # Cart product successful removal
        request = self.factory.delete('/products/cart', {
            'cart_product_id': cart_products[0].id,
            'quantity': cart_products[0].quantity
        })
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200, 'Remove from cart failed')

    def test_orders(self):
        """
            This will test all the orders api.
        """
        user = self.user
        view = InitiateOrderCartView.as_view()

        request = self.factory.get('/products/order/initiate')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200, 'Initiate Order Failed')

        customer_order_id = response.data['data']['order']['customer_order_id']
        amount = response.data['data']['order']['amount_payable']

        view = InitiatePaymentView.as_view()
        request = self.factory.post('/products/order/initiate/payment', {
            'payment_type': 'c'
        }, format='json')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 400, 'Validation check failed for customer_order_id')

        request = self.factory.post('/products/order/initiate/payment', {
            'customer_order_id': 'c'
        }, format='json')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 400, 'Validation check failed for payment_type')

        request = self.factory.post('/products/order/initiate/payment', {
            'customer_order_id': 'c',
            'payment_type': 'c'
        }, format='json')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 400, 'Validation check failed for customer_order_id')

        request = self.factory.post('/products/order/initiate/payment', {
            'customer_order_id': customer_order_id,
            'payment_type': 'U'
        }, format='json')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200, 'Initiate Payment Failed.')

        view = CallbackByPaymentGatewayView.as_view()

        request = self.factory.post('/products/callback/by/payment/gateway', {
            'amount_paid': amount,
            'payment_status': 'CONFIRMED'
        }, format='json')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 400, 'Validation check failed for customer_order_id')

        request = self.factory.post('/products/callback/by/payment/gateway', {
            'customer_order_id': customer_order_id,
            'payment_status': 'CONFIRMED'
        }, format='json')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 400, 'Validation check failed for amount_paid')

        request = self.factory.post('/products/callback/by/payment/gateway', {
            'customer_order_id': customer_order_id,
            'amount_paid': amount
        }, format='json')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 400, 'Validation check failed for payment_status')

        request = self.factory.post('/products/callback/by/payment/gateway', {
            'customer_order_id': customer_order_id,
            'amount_paid': amount,
            'payment_status': 'CONFIRMED'
        }, format='json')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200, 'Payment Callback APi failed')

        view = CancelOrderView.as_view()
        request = self.factory.post('/products/order/cancel', {
            'id': 1
        }, format='json')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200, 'Cancel Order failed')

        view = ViewAllOrders.as_view()
        request = self.factory.get('/products/order/view/all')
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 403, 'Admin Check Failed')

        request = self.factory.get('/products/order/view/all')
        force_authenticate(request, user=self.admin_user)
        response = view(request)
        self.assertEqual(response.status_code, 200, 'View Order failed')
