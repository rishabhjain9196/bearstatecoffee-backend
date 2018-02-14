from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.serializers import ProductSerializer
from products.models import Products


class ProductsView(APIView):
    """
        Used for manipulating the data in the products table.
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        query_set = Products.objects.all()
        serializer = ProductSerializer(query_set, many=True)
        return Response(serializer.data)


class EditProducts(APIView):

    # Remove these after authenticating
    authentication_classes = ()
    permission_classes = ()

    def get_product(self, pk):
        try:
            return Products.objects.get(pk=pk)
        except Products.DoesNotExist:
            raise Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        # Pending Authentication of Super user
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        print(pk)
        # Pending Authentication of Super user
        product = self.get_product(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
