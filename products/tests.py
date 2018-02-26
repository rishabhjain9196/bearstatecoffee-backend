from django.test import TestCase
from products.models import Products


class ProductsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        total_products = 30
        for counter in range(total_products):
            Products.objects.create(name='Product %s' % counter, image="Random URL", cost=50.00, avail_quantity=100,
                                    desc='Sample Desc')

    def setUp(self):
        pass

    def test_view_all_products(self):
        resp = self.client.get('/products/view')
        self.assertEqual(resp.status_code, 200)

    def tearDown(self):
        pass
