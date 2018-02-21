from rest_framework.response import Response
from rest_framework import status
from products.models import Products, Combo, CartProducts
from products.serializers import ProductSerializer, ComboSerializer, CartProductSerializer


def add_product(data):
    """
        Utility function to add product
    """
    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def fetch_all_products():
    """
        Utility function to get all products
    """
    query_set = Products.objects.all(is_delete=False)
    serializer = ProductSerializer(query_set, many=True)
    return serializer.data


def update_product(data, key):
    """
        Utility Function to update a given product by it's key.
    """
    product = Products.objects.filter(pk=key, is_delete=False).first()
    if not product:
        return Response({'status': 'product does not exist'}, status=status.HTTP_400_BAD_REQUEST)

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
    """
    product = Products.objects.filter(pk=key, is_delete=False).first()
    if not product:
        return Response({'status': 'product does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    setattr(product, "is_delete", True)
    product.save()
    return Response({'status': 'deleted'}, status=status.HTTP_200_OK)


def create_combo(combo):
    """
        Utility function to create a combo product.
    """
    total_quantity = 0
    for products in combo["quantity"]:
        total_quantity = total_quantity + combo["quantity"][products]
    if total_quantity < 2:
        return {'status': 'number of products must at least be two.'}
    combo_name = combo["name"]
    combo_image = combo["image"]
    combo_cost = combo["cost"]
    combo_avail_quantity = combo["avail_quantity"]
    combo_desc = combo["desc"]
    new_combo = Products.objects.create(name=combo_name, image=combo_image,
                                        cost=combo_cost, avail_quantity=combo_avail_quantity,
                                        desc=combo_desc
                                        )
    new_combo.is_combo = True
    new_combo.save()
    for product_id in combo["quantity"]:
        product = Products.objects.filter(pk=int(product_id), is_delete=False).first()
        if not product:
            return {"status: one or more product in the list does not exist"}
        m1 = Combo(combo=new_combo, product=product, quantity=combo["quantity"][product_id])
        m1.save()
    return {'status': 'created new combo'}


def view_all_combos():
    """
        Utility function to view all combo products along with the quantity of sub-products
    """
    all_combos = Products.objects.filter(is_combo=True, is_delete=False)
    serialized_data = ProductSerializer(all_combos, many=True)
    counter = 0
    for obj in all_combos:
        product_ids = obj.combo_product_ids.all()
        serialized_data.data[counter]['combo_ids'] = {}
        for num in product_ids:
            ser_data = ProductSerializer(num)
            quan = Combo.objects.filter(combo=serialized_data.data[counter]["pk"],
                                        product=int(ser_data.data["pk"]))
            ser_quan = ComboSerializer(quan, many=True)
            serialized_data.data[counter]['combo_ids'][ser_data.data["pk"]] = ser_quan.data[0]['quantity']
        counter += 1
    return serialized_data.data


def add_product_to_cart(user, data):
    """
        Helper function to add product to cart.
    :param user: user instance fetched from the request.
    :param data: data fetched from the request, which should have product_id, and quantity.
    :return: True or false, with appropriate message.
    """
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not (product_id and quantity):
        return Response({'result': False, 'message': 'product_id or quantity missing.'},
                        status=status.HTTP_400_BAD_REQUEST)

    product = Products.objects.filter(id=product_id, is_delete=False).first()

    if product:
        if product.avail_quantity >= quantity:
            cart_product = CartProducts.objects.create(user=user, product=product, quantity=quantity)
            print(cart_product)
            payload = {
                'result': True,
                'data': CartProductSerializer(instance=cart_product).data
            }
            return Response(payload)
        else:
            return Response({'result': False, 'message': 'Available quantity is '+str(quantity)},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'result': False, 'message': 'No product found'}, status=status.HTTP_400_BAD_REQUEST)
