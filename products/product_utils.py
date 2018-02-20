from rest_framework.response import Response
from rest_framework import status

from products.models import Products, Combo
from products.serializers import ProductSerializer, ComboSerializer


def add_product(data):
    """
        Utility function to add product
        :param  data: JSON object in the format of products model to add in product.
        :return response status 201 and serialized data, if data passed is valid,
        otherwise return error with status 400.
    """
    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def fetch_all_products():
    """
        Utility function to get all products
        :return JSON formatted data of all single products (not combos) that are not deleted.
    """
    query_set = Products.objects.filter(is_delete=False, is_combo=False)
    serializer = ProductSerializer(query_set, many=True)
    return serializer.data


def update_product(data, key):
    """
        Utility Function to update a given product by it's key.
        :param  data: JSON formatted data to update product
        :param key: Primary key of the product to be updated
        :return A response with either updated (status = 200) or does not exist (status = 404)
    """
    product = Products.objects.filter(pk=key, is_delete=False).first()
    if not product:
        return Response({'status': 'product does not exist'}, status=status.HTTP_404_NOT_FOUND)

    valid_fields = ['name', 'image', 'cost', 'avail_quantity', 'desc', 'rating', 'users_rated', 'is_combo',
                    'is_delete']
    for field in data:
        if field in valid_fields:
            setattr(product, field, data[field])
    product.save()
    return Response({'status': 'updated'}, status=status.HTTP_200_OK)


def delete_product(key):
    """
        Utility function to mark a product as deleted
        :param key: Primary key of the product to be deleted
        :return A response with either deleted (status = 200) or does not exist (status = 404)
    """
    product = Products.objects.filter(pk=key, is_delete=False).first()
    if not product:
        return Response({'status': 'product does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    setattr(product, 'is_delete', True)
    product.save()
    return Response({'status': 'deleted'}, status=status.HTTP_200_OK)


def create_combo(combo):
    """
        Utility function to create a combo product.
        :param combo: JSON Object with product model format, added quantity field - which has a dictionary of product
        ids with their respective quantity
        :return A response with either created (status = 200) or error in data (status = 400)
    """
    total_quantity = 0
    for products in combo.get('quantity'):
        total_quantity = total_quantity + combo.get('quantity').get(products)
    if total_quantity < 2:
        return Response({'status': 'number of products must at least be two.'}, status=status.HTTP_400_BAD_REQUEST)
    combo_name = combo.get('name')
    combo_image = combo.get('image', '')
    combo_cost = combo.get('cost')
    combo_avail_quantity = combo.get('avail_quantity', 1)
    combo_desc = combo.get('desc', '')
    if not combo_name or not combo_cost:
        return Response({'status': 'Name and Cost required for combo'}, status=status.HTTP_400_BAD_REQUEST)

    new_combo = Products.objects.create(name=combo_name, image=combo_image,
                                        cost=combo_cost, avail_quantity=combo_avail_quantity,
                                        desc=combo_desc
                                        )
    new_combo.is_combo = True
    new_combo.save()
    for product_id in combo['quantity']:
        product = Products.objects.filter(pk=int(product_id), is_delete=False).first()
        if not product:
            return Response({'status': 'one or more product in the list does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
        combo_relation = Combo(combo=new_combo, product=product, quantity=combo['quantity'][product_id])
        combo_relation.save()
    return Response({'status': 'created new combo'}, status=status.HTTP_200_OK)


def view_all_combos():
    """
        Utility function to view all combo products along with the quantity of sub-products
        :return JSON formatted serialized data of product combo with added combo_ids field having information
        regarding the primary keys of contained products.
    """
    all_combos = Products.objects.filter(is_combo=True, is_delete=False)
    serialized_data = ProductSerializer(all_combos, many=True)
    for counter, obj in enumerate(all_combos):
        product_ids = obj.combo_product_ids.all()
        serialized_data.data[counter]['combo_ids'] = {}
        for num in product_ids:
            ser_data = ProductSerializer(num)
            quan = Combo.objects.filter(combo=serialized_data.data[counter]['pk'],
                                        product=int(ser_data.data['pk']))
            ser_quan = ComboSerializer(quan, many=True)
            serialized_data.data[counter]['combo_ids'][ser_data.data['pk']] = ser_quan.data[0]['quantity']
    return serialized_data.data
