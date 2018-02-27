from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from products.models import Products, Categories
from accounts.models import MyUser
from products.views import EditProductsView, EditProductCategoriesView, EditCategoriesView, ProductCategoriesView


class ProductsViewTest(TestCase):

    factory = APIRequestFactory()
    admin_user = MyUser.objects.filter(is_verified=True, is_staff=True, is_superuser=True).first()
    user = MyUser.objects.all().first()

    @classmethod
    def setUpTestData(cls):
        total_products = 30
        total_users = 50
        for counter in range(total_products):
            Products.objects.create(name='Product %s' % counter, image='Random URL', cost=50.00, avail_quantity=100,
                                    desc='Sample Desc')

        MyUser.objects.create_superuser(email='rishabh.jain@kuliza.com', password='qwerty',
                                        is_verified=True, phone_number='8744985115', first_name='Rishabh',
                                        last_name='Jain')

        Categories.objects.create(pk=2, period_number=1, period_name='Daily', terms='Sample terms')
        Categories.objects.create(pk=3, period_number=2, period_name='Daily', terms='Sample terms 2')
        Categories.objects.create(pk=4, period_number=2, period_name='Daily', terms='Sample terms 2')

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

        product = Products.objects.get(pk=7)
        category = Categories.objects.get(pk=4)
        product.category_ids.add(category)
        product.save()

    def setUp(self):
        pass

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

    def tearDown(self):
        pass
