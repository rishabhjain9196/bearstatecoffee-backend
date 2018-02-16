from rest_framework.response import Response
from rest_framework import status
from products.serializers import CategoriesSerializer
from products.models import Categories, Products


def fetch_all_categories():
    query_set = Categories.objects.all()
    serializer = CategoriesSerializer(query_set, many=True)
    return serializer.data


def add_category(data):
    serializer = CategoriesSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def update_category(data, key):
    try:
        category = Categories.objects.get(pk=key)
    except Products.DoesNotExist:
        return Response({'STATUS': 'ITEM DOES NOT EXIST'}, status=status.HTTP_404_NOT_FOUND)

    valid_fields = ['period_number', 'period_name', 'terms']
    for field in data:
        if field in valid_fields:
            setattr(category, field, data[field])
    category.save()
    return Response({'STATUS': 'UPDATED'}, status=status.HTTP_200_OK)


def delete_category(key):
    try:
        category = Categories.objects.get(pk=key)
    except Products.DoesNotExist:
        return Response({'STATUS': 'ITEM DOES NOT EXIST'}, status=status.HTTP_404_NOT_FOUND)
    category.delete()
    return Response({'STATUS': 'DELETED'}, status=status.HTTP_200_OK)


def get_all_categories_of_product(key):
    product = Products.objects.get(pk=key)
    ser = CategoriesSerializer(product.category_ids.all(), many=True)
    return Response(ser.data, status=status.HTTP_200_OK)


def add_category_to_product(product_pk, category_pk):
    product = Products.objects.get(pk=product_pk)
    category = Categories.objects.get(pk=category_pk)
    product.category_ids.add(category)
    return Response(status=status.HTTP_201_CREATED)


def remove_category_from_product(product_pk, category_pk):
    product = Products.objects.get(pk=product_pk)
    category = Categories.objects.get(pk=category_pk)
    product.category_ids.remove(category)
    return Response(status=status.HTTP_200_OK)
