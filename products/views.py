from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from products import product_utils, categories_util
import products.constants as const


class ProductsView(APIView):
    """
        GET: For viewing all products
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        return Response(product_utils.fetch_all_products())


class EditProductsView(APIView):
    """
        POST: To add a new product
        DELETE: To delete an existing product
        PATCH: To update an existing product
    """
    # Pending authentication from Super user, Edit next two lines after that.
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        data = request.data
        return product_utils.add_product(data)

    def delete(self, request, pk):
        return product_utils.delete_product(pk)

    def patch(self, request, pk):
        data = request.data
        return product_utils.update_product(data, pk)


class ProductCategoriesView(APIView):
    """
        GET: For viewing all available categories for a product
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, pk):
        return categories_util.get_all_categories_of_product(pk)


class EditProductCategoriesView(APIView):
    """
        GET: To add a category to a product
        POST: To delete an existing category from a product
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, pk, cat_pk):
        return categories_util.add_category_to_product(pk, cat_pk)

    def post(self, request, pk, cat_pk):
        return categories_util.remove_category_from_product(pk, cat_pk)


class CategoriesView(APIView):
    """
        GET: To get all available categories irrespective of the product
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        return Response(categories_util.fetch_all_categories())


class EditCategoriesView(APIView):
    """
        POST: Function to insert data into the categories table.
        DELETE: Function to delete a category using it's primary key.
        PATCH: This function updates a category with given primary key
    """
    # Pending authentication from Super user, Edit next two lines after that.
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        data = request.data
        return categories_util.add_category(data)

    def delete(self, request, pk):
        return categories_util.delete_category(pk)

    def patch(self, request, pk):
        data = request.data
        return categories_util.update_category(data, pk)


class ComboView(APIView):
    """
    GET: To view all combos
    POST: Create a combo by passing a JSON request
    """
    # Pending authentication from Super user, Edit next two lines after that.
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        return Response(product_utils.view_all_combos())

    def post(self, request):
        return Response(product_utils.create_combo(request.data))


class CartView(APIView):
    """
        This will help in displaying, adding product, removing product from cart
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return product_utils.get_the_user_cart(request.user)

    def post(self, request):
        return product_utils.add_product_to_cart(request.user, request.data)

    def delete(self, request):
        cart_product_id = request.data.get('cart_product_id', '')
        quantity = request.data.get('quantity', '')

        if not (cart_product_id and quantity):
            return Response({'result': False, 'message': const.CART_VALIDATION},
                            status=status.HTTP_400_BAD_REQUEST)

        return product_utils.remove_from_cart(request.user, cart_product_id, quantity)


class InitiateOrderCartView(APIView):
    """
        This will place initiate the order using the active cart products.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return product_utils.initiate_order_from_cart(request.user)


class InitiatePaymentView(APIView):
    """
        This will help in initiating the payment.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        return product_utils.initiate_payment(request.data)


class CallbackByPaymentGatewayView(APIView):
    """
        This will be the callback received by the payment gateway to confirm the payment.
    """
    permission_classes = ()

    def post(self, request):
        return product_utils.confirm_payment(request.data)


class GetOrderView(APIView):
    """
        This will fetch the orders placed by user.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return product_utils.get_order_of_user(request.user)


class CancelOrderView(APIView):
    """
        This will cancel the order.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        return product_utils.cancel_order(request.user, request.data.get('id', ''))


class ViewAllOrders(APIView):
    """
        This will help in viewing all the orders.
    """
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        return product_utils.view_all_orders()
