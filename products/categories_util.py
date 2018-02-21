from rest_framework.response import Response
from rest_framework import status

from products.serializers import CategoriesSerializer
from products.models import Categories, Products


def fetch_all_categories():
    """
        Utility function to get all the categories
        :return JSON data containing all the categories
    """
    query_set = Categories.objects.all()
    serializer = CategoriesSerializer(query_set, many=True)
    return serializer.data


def add_category(data):
    """
        Utility function to Add a new category option
        :param data: Data of the category that has to be added.
        :return: Response whether the data was added(status = 201) or not(status= 400)
    """
    serializer = CategoriesSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def update_category(data, key):
    """
        Utility function to update an existing category
        :param data: Data of the category that has to be updated.
        :return: Response whether the data was updated(status = 200) or not(status= 404)
    """
    category = Categories.objects.filter(pk=key).first()
    if not category:
        return Response({'STATUS': 'CATEGORY NOT FOUND'}, status=status.HTTP_404_NOT_FOUND)
    valid_fields = ['period_number', 'period_name', 'terms']
    correct_details = True
    for field in data:
        if field in valid_fields:
            setattr(category, field, data[field])
        else:
            correct_details = False
            break
    if correct_details:
        category.save()
        return Response({'STATUS': 'UPDATED'}, status=status.HTTP_200_OK)
    return Response({'STATUS': 'FIELD NOT FOUND'}, status=status.HTTP_404_NOT_FOUND)


def delete_category(key):
    """
        Utility function to delete category
        :param key: Primary key of the category to be deleted
        :return: Response whether the data was added(status = 200) or not(status= 404)
    """
    category = Categories.objects.filter(pk=key).first()
    if not category:
        return Response({'STATUS': 'CATEGORY NOT FOUND'}, status=status.HTTP_404_NOT_FOUND)
    setattr(category, 'is_delete', True)
    category.save()
    return Response({'STATUS': 'DELETED'}, status=status.HTTP_200_OK)


def get_all_categories_of_product(key):
    """
        Utility function to get available categories of a given product
        :param key: Primary key of the product for which categories are to be fetched.
        :return: Response whether the data was successfully fetched(status = 200) or not(status= 404)
    """
    product = Products.objects.filter(pk=key).first()
    if not product:
        return Response({'STATUS': 'UNAVAILABLE PRODUCT'}, status=status.HTTP_404_NOT_FOUND)
    ser = CategoriesSerializer(product.category_ids.all(), many=True)
    return Response(ser.data, status=status.HTTP_200_OK)


def add_category_to_product(product_pk, category_pk):
    """
        Utility function to add a category to a given product
        :param product_pk: Primary key of a product to which category is to be added.
        :param category_pk: Primary key of Category which is to be added.
        :return: Response whether the data was added(status = 201) or not(status= 404)
    """
    product = Products.objects.filter(pk=product_pk).first()
    category = Categories.objects.filter(pk=category_pk).first()
    if not product or not category:
        return Response({'STATUS': 'UNAVAILABLE PRODUCT OR CATEGORY'}, status=status.HTTP_404_NOT_FOUND)
    product.category_ids.add(category)
    return Response({'STATUS': 'ADDED CATEGORY'}, status=status.HTTP_201_CREATED)


def remove_category_from_product(product_pk, category_pk):
    """
        Utility function to remove a category from a given product
        :param product_pk: Primary key of a product to which category is to be removed.
        :param category_pk: Primary key of Category which is to be removed.
        :return: Response whether the data was removed(status = 200) or not(status= 404)
    """
    product = Products.objects.filter(pk=product_pk).first()
    category = Categories.objects.filter(pk=category_pk).first()
    if not product or not category:
        return Response({'STATUS': 'UNAVAILABLE PRODUCT OR CATEGORY'}, status=status.HTTP_404_NOT_FOUND)
    product.category_ids.remove(category)
    return Response({'STATUS': 'DELETED CATEGORY'}, status=status.HTTP_200_OK)
