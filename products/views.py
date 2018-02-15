from rest_framework.views import APIView
from rest_framework.response import Response
from products import utils


class ProductsView(APIView):
    """
        Used for manipulating the data in the products table.
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        """
            This function fetches all the products in the Products Model.
        """
        return Response(utils.fetch_all_products())


class EditProducts(APIView):

    # Pending authentication from Super user, Remove next two lines after that.
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        """
            Function to insert data into the products table.
        """
        data = request.data
        return utils.insert(data)

    def delete(self, request, pk):
        """
            Function to delete a product using it's primary key.
        """
        return utils.delete(pk)

    def patch(self, request, pk):
        """
            This function updates a product with given primary key
        """
        data = request.data
        return utils.update(data, pk)

