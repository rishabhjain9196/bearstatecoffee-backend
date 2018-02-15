from rest_framework.response import Response
from rest_framework import status
from products.models import Products
from products.serializers import ProductSerializer


def insert(data):
    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def fetch_with_pk(key):
    try:
        return Products.objects.get(pk=key)
    except Products.DoesNotExist:
        raise Response({'STATUS': 'ITEM DOES NOT EXIST'}, status=status.HTTP_404_NOT_FOUND)


def fetch_all_products():
    query_set = Products.objects.all()
    serializer = ProductSerializer(query_set, many=True)
    return serializer.data


def update(data, key):
    product = fetch_with_pk(key)
    valid_fields = ['name', 'image', 'cost', 'avail_quantity', 'desc', 'rating', 'users_rated', 'is_combo',
                    'is_delete']
    for field in data:
        if field in valid_fields:
            setattr(product, field, data[field])
    product.save()
    return Response({'STATUS': 'UPDATED'}, status=status.HTTP_200_OK)


def delete(key):
    product = fetch_with_pk(key)
    if product.is_delete:
        return Response({'STATUS': 'ITEM DOES NOT EXIST'}, status=status.HTTP_404_NOT_FOUND)
    setattr(product, "is_delete", True)
    product.save()
    return Response({'STATUS': 'DELETED'}, status=status.HTTP_204_NO_CONTENT)
