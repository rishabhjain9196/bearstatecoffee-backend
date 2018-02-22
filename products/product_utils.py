from django.db.models import F, FloatField, ExpressionWrapper
from rest_framework.response import Response
from rest_framework import status
from products.models import Products, Combo, CartProducts, Orders
from products.serializers import ProductSerializer, ComboSerializer, CartProductSerializer, OrdersSerializers
from accounts.utils import send_text_email


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
    cart_product = CartProducts.objects.filter(user=user, product=product, is_active=True).first()

    if product:
        if cart_product and (cart_product.quantity+quantity <= product.avail_quantity):
            cart_product.quantity += quantity
            cart_product.save()
            payload = {
                'result': True,
                'data': CartProductSerializer(instance=cart_product).data
            }
            return Response(payload)
        elif product.avail_quantity >= quantity:
            cart_product = CartProducts.objects.create(user=user, product=product, quantity=quantity)
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


def get_the_user_cart(user):
    """
        Helper function to fetch the cart.
    :param user: user fetched from request.
    :return: True or False with cart products.
    """
    cart_products = CartProducts.objects.filter(user=user, is_active=True).annotate(
        cost=ExpressionWrapper(F('quantity')*F('product__cost'), output_field=FloatField()))
    payload = {
        'result': True,
        'data': CartProductSerializer(instance=cart_products, many=True).data
    }

    return Response(payload, status=status.HTTP_200_OK)


def remove_from_cart(user, cart_product_id, quantity):
    """
        Helper function to remove quantity from cart.
    :param user: User fetched from request.
    :param cart_product_id: cart Id of the product.
    :param quantity: Quantity that need to be removed.
    :return: True or false, with appropriate message.
    """
    cart_product = CartProducts.objects.filter(user=user, is_active=True, pk=cart_product_id).first()

    if cart_product:
        cart_product.quantity -= quantity
        if cart_product.quantity <= 0:
            cart_product.is_active = False
        cart_product.save()
        return Response({'result': True, 'data': 'Removed'})
    else:
        return Response({'result': False, 'message': 'Product doesn\'t exist in cart.'},
                        status=status.HTTP_400_BAD_REQUEST)


def initiate_order_from_cart(user):
    """
        This will just initiate the order for the user.
    :param user: User fetched from request.
    :return: True or false, with Customer_ID.
    """
    cart_products = CartProducts.objects.filter(user=user, is_active=True,
                                                product__avail_quantity__gte=F('quantity')).annotate(
        cost=ExpressionWrapper(F('quantity') * F('product__cost'), output_field=FloatField()))
    cost = 0

    if len(cart_products) == 0:
        return Response({'result': False, 'message': 'Cart products not available to buy.'},
                        status=status.HTTP_400_BAD_REQUEST)

    for product in cart_products:
        cost += product.cost
        product.product.avail_quantity -= product.quantity
        product.product.save()

    order = Orders.objects.create(user=user, is_subscription=False, amount_payable=cost)

    payload = {
        'result': True,
        'data': {
            'cart_products': CartProductSerializer(instance=cart_products, many=True).data,
            'order': OrdersSerializers(instance=order).data,
            'total_cost': cost
        }
    }
    cart_products.update(order=order, is_active=False)

    return Response(payload, status=status.HTTP_200_OK)


def send_mail_on_order_confirmation(customer_order_id):
    """
        Helper Function to send the email to user for their confirmed user.
    :param customer_order_id:
    :return:
    """
    order = Orders.objects.filter(customer_order_id=customer_order_id).first()
    if order.is_subscription:
        pass
    else:
        body = 'Your order is confirmed amounting to ' + str(order.amount_payable) + ' with Customer Order Id ' + str(
            customer_order_id) + '.\n'
        cart_products = order.cartproducts_set.all()
        body += 'Product      Quantity      Price\n'
        for product in cart_products:
            body += '%s      %s      %s\n' % (
                product.product.name, str(product.quantity), str(product.quantity * product.product.cost))
        subject = 'Your Order is Confirmed.'
        send_text_email(body=body, subject=subject, to_address=product.user.email)


def initiate_payment(data):
    """
        This will update the payment details and initiate payment if necessary.
    :param user: User fetched from request.
    :param data: It must have cust_order_id, payment_type.
    :return: True or false, with Customer_ID.
    """
    payment_type = data.get('payment_type', '')
    customer_order_id = data.get('customer_order_id', '')
    if payment_type and customer_order_id:
        if payment_type == 'C':
            Orders.objects.filter(customer_order_id=customer_order_id).update(is_confirmed=True,
                                                                              payment_type=payment_type)
            send_mail_on_order_confirmation(customer_order_id)
        else:
            Orders.objects.filter(customer_order_id=customer_order_id).update(payment_type=payment_type)

        payload = {
            'result': True
        }
        return Response(payload, status=status.HTTP_200_OK)
    else:
        return Response({'result': False, 'message': 'customer_order_id or payment_type missing'},
                        status=status.HTTP_400_BAD_REQUEST)


def confirm_order(data):
    """
        Helper function to be called as the response against the callback of the payment gateway.
    :param data: It must contains customer_order_id, amount_paid, payment_status.
    :return: True or false, with desired response.
    """
    customer_order_id = data.get('customer_order_id', '')
    amount_paid = data.get('amount_paid', '')
    payment_status = data.get('payment_status', '')

    if payment_status and customer_order_id and amount_paid:
        if payment_status == 'CONFIRMED':
            print('dsfjdsfhjsd')
            Orders.objects.filter(customer_order_id=customer_order_id).update(amount_paid=amount_paid,
                                                                              payment_status=True,
                                                                              is_confirmed=True)
            send_mail_on_order_confirmation(customer_order_id)
        else:
            order = Orders.objects.filter(customer_order_id=customer_order_id).first()
            cart_products = order.cartproducts_set.all()

            for product in cart_products:
                product.product.avail_quantity += product.quantity
                product.product.save()

            order.payment_status = payment_status
            order.save()
        return Response({'result': True}, status=status.HTTP_200_OK)
    else:
        return Response({'result': False, 'message': 'customer_order_id or payment_status or amount_paid missing'},
                        status=status.HTTP_400_BAD_REQUEST)


def get_order_of_user(user):
    """
        This will fetch the order list of user.
    :param user:
    :return:
    """
    payload = {
        'result': True,
        'data': OrdersSerializers(instance=Orders.objects.filter(user=user), many=True).data
    }
    return Response(payload, status=status.HTTP_200_OK)
