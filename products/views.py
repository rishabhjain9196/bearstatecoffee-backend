from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from products import product_utils, categories_util


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
    # Pending custom authentication from Super user, Edit next line after that.
    permission_classes = (permissions.IsAdminUser,)

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
    permission_classes = ()

    def get(self, request, pk):
        return categories_util.get_all_categories_of_product(pk)


class EditProductCategoriesView(APIView):
    """
        GET: To add a category to a product
        POST: To delete an existing category from a product
    """
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, pk, cat_pk):
        return categories_util.add_category_to_product(pk, cat_pk)

    def delete(self, request, pk, cat_pk):
        return categories_util.remove_category_from_product(pk, cat_pk)


class CategoriesView(APIView):
    """
        GET: To get all available categories irrespective of the product
    """
    permission_classes = ()

    def get(self, request):
        return Response(categories_util.fetch_all_categories())


class EditCategoriesView(APIView):
    """
        POST: Function to insert data into the categories table.
        DELETE: Function to delete a category using it's primary key.
        PATCH: This function updates a category with given primary key
    """
    permission_classes = (permissions.IsAdminUser,)

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
    """
    permission_classes = ()

    def get(self, request):
        return Response(product_utils.view_all_combos())


class EditComboView(APIView):
    """
    POST: To create a new combo
    """
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        return Response(product_utils.create_combo(request.data))



