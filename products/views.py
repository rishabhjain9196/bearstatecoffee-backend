from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from products import product_utils, categories_util, subscription_utils


class ProductsView(APIView):
    """
        GET: For viewing all products
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        """
        :return: Response containing JSON data, with all the details of single products.
        """
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
        """
        :param request: Request object with the data of the product to be added.
        :return: Response whether the product was successfully added (status = 201) or not (status = 400).
        """
        data = request.data
        return product_utils.add_product(data)

    def delete(self, request, pk):
        """
        :param pk: Product Key of the Product to delete
        :return: Response whether the product was successfully deleted (status = 200) or not (status = 400).
        """
        return product_utils.delete_product(pk)

    def patch(self, request, pk):
        """
        :param request: JSON Formatted data to be updated
        :param pk: Primary key of the product to be updated
        :return: Response whether the product was successfully updated (status = 200) or not (status = 400).
        """
        data = request.data
        return product_utils.update_product(data, pk)


class ProductCategoriesView(APIView):
    """
        GET: For viewing all available categories for a product
    """
    permission_classes = ()

    def get(self, request, pk):
        """
        :param pk: Primary key of whose the categories are to be fetched.
        :return: Response of status 200 and serialized data containing all the categories available for the product,
        Response of status 404, if the product is not found.
        """
        return categories_util.get_all_categories_of_product(pk)


class EditProductCategoriesView(APIView):
    """
        GET: To add a category to a product
        POST: To delete an existing category from a product
    """
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, pk, cat_pk):
        """
        :param pk: Primary Key of te product
        :param cat_pk: Primary key of the category
        :return: Response whether the category was successfully added to the product(status = 201),
        or not(status = 404).
        """
        return categories_util.add_category_to_product(pk, cat_pk)

    def delete(self, request, pk, cat_pk):
        """
        :param pk: Primary key of the product
        :param cat_pk: Primary Key of the category
        :return: Response whether the category was successfully removed from the product(status= 200),
        or not(status= 404).
        """
        return categories_util.remove_category_from_product(pk, cat_pk)


class CategoriesView(APIView):
    """
        GET: To get all available categories irrespective of the product
    """
    permission_classes = ()

    def get(self, request):
        """
        :return: Response with JSON data, containing all the categories data.
        """
        return Response(categories_util.fetch_all_categories())


class EditCategoriesView(APIView):
    """
        POST: Function to insert data into the categories table.
        DELETE: Function to delete a category using it's primary key.
        PATCH: This function updates a category with given primary key
    """
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        """
        :param request: Request object with data of a new category that has to be added.
        :return: Response whether the data was successfully added(status= 201) or not(status= 400).
        """
        data = request.data
        return categories_util.add_category(data)

    def delete(self, request, pk):
        """
        :param pk: Primary key of the category that has to be deleted.
        :return: Response whether the data was successfully deleted(status= 200) or not(status= 404).
        """
        return categories_util.delete_category(pk)

    def patch(self, request, pk):
        """
        :param request: Request object containing the data that has to be updated.
        :param pk: Primary key of the category that has to be updated.
        :return: Response whether the data was successfully updated(status= 200) or not(status= 404).
        """
        data = request.data
        return categories_util.update_category(data, pk)


class ComboView(APIView):
    """
    GET: To view all combos
    """
    permission_classes = ()

    def get(self, request):
        """
        :return: Response with JSON data having all the combo data, along with the quantities
        of the products inside them.
        """
        return product_utils.view_all_combos()


class EditComboView(APIView):
    """
        POST: To create a new combo
    """
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        """
        :param request: Request object containing data to create a combo, along with the quantities of the products
        inside.
        :return: Response whether the data was successfully added(status= 200) or not(status= 400).
        """
        return product_utils.create_combo(request.data)


class Subscription(APIView):
    """
        GET: To view all subscriptions by a user
        POST: Add a subscription to a user
        PUT: Finalize subscription
        PATCH: Shift/Update Subscription
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """
        :return: Response will the JSON data of all the subscriptions of the user.
        """
        user_id = request.user.pk
        return subscription_utils.view_subscription(user_id)

    def post(self, request):
        """
        :param request: Data to add a subscription along with user's primary key
        :return: Response whether the data was added successfully(status= 200) or
        not(status = 400)
        """
        user = request.user
        return subscription_utils.add_subscription(user, request.data)

    def put(self, request):
        """
        :param request: Data regarding the order dates of the subscription
        :return: Response whether the subscription was able to be finalized or not.
        """
        user = request.user
        subscription_id = request.data[0]['subscription_id']
        data = request.data[1]
        return subscription_utils.finalize_subscription(user, subscription_id, data)


class CheckSubscriptions(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        """
        :return: Returns all subscriptions that have their nex order in a week.
        """
        return subscription_utils.check_for_new_orders()
