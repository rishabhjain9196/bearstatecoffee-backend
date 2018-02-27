from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, FloatField, ExpressionWrapper

from rest_framework.response import Response
from rest_framework import status

from accounts.utils import send_text_email
from products.models import Products, Combo, CartProducts, Orders
from products.serializers import ProductSerializer, ComboSerializer, CartProductSerializer, OrdersSerializers
from products.constants import *


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
    return Response(serializer.data)


def update_product(data, key):
    """
        Utility Function to update a given product by it's key.
        :param  data: JSON formatted data to update product
        :param key: Primary key of the product to be updated
        :return A response with either updated (status = 200), does not exist (status = 404) or Bad Request(status=400)
    """
    try:
        product = Products.objects.get(pk=key, is_delete=False)
    except ObjectDoesNotExist:
        return Response({'status': PRODUCT_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

    valid_fields = ['name', 'image', 'cost', 'avail_quantity', 'desc']

    for field in data:
        if field in valid_fields:
            setattr(product, field, data[field])
        else:
            return Response({'status': INVALID_FIELDS}, status=status.HTTP_400_BAD_REQUEST)
    product.save()
    return Response({'status': PRODUCT_UPDATED}, status=status.HTTP_200_OK)


def delete_product(key):
    """
        Utility function to mark a product as deleted
        :param key: Primary key of the product to be deleted
        :return A response with either deleted (status = 200) or does not exist (status = 404)
    """
    try:
        product = Products.objects.get(pk=key, is_delete=False)
    except ObjectDoesNotExist:
        return Response({'status': PRODUCT_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)

    setattr(product, 'is_delete', True)
    product.save()
    return Response({'status': PRODUCT_DELETED}, status=status.HTTP_200_OK)


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
        return Response({'status': COMBO_QUANTITY_ERROR},
                        status=status.HTTP_400_BAD_REQUEST)
    combo_name = combo.get('name')
    combo_image = combo.get('image', '')
    combo_cost = combo.get('cost')
    combo_avail_quantity = combo.get('avail_quantity', 1)
    combo_desc = combo.get('desc', '')
    if not combo_name or not combo_cost:
        return Response({'status': COMBO_FIELD_ERROR},
                        status=status.HTTP_400_BAD_REQUEST)

    new_combo = Products.objects.create(name=combo_name, image=combo_image,
                                        cost=combo_cost, avail_quantity=combo_avail_quantity,
                                        desc=combo_desc, is_combo=True
                                        )

    # Check if combo products exists
    for product_id in combo['quantity']:
        try:
            product = Products.objects.get(pk=int(product_id), is_delete=False)
        except ObjectDoesNotExist:
            return Response({'status': COMBO_PRODUCT_ERROR},
                            status=status.HTTP_404_NOT_FOUND)

    new_combo.save()

    for product_id in combo['quantity']:
        combo_relation = Combo(combo=new_combo, product=product, quantity=combo['quantity'][product_id])
        combo_relation.save()

    return Response({'status': COMBO_ADDED}, status=status.HTTP_200_OK)


def view_all_combos():
    """
        Utility function to view all combo products along with the quantity of sub-products
        :return A response with JSON formatted serialized data of product combo with added combo_ids field having information
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
    return Response(serialized_data.data)


def add_product_to_cart(user, data):
    """
        Helper function to add product to cart.
    :param user: user instance fetched from the request.
    :param data: data fetched from the request, which should have product_id, and quantity.
    :return: True or false, with appropriate message.
    """
    product_id = int(data.get('product_id', '0'))
    quantity = int(data.get('quantity', '0'))

    if not (product_id and quantity):
        return Response({'result': False, 'message': ADD_TO_CART_VALIDATION},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Products.objects.get(pk=product_id, is_delete=False)
    except ObjectDoesNotExist:
        return Response({'result': False, 'message': INVALID_PRODUCT}, status=status.HTTP_400_BAD_REQUEST)

    cart_product = CartProducts.objects.filter(user=user, product=product, is_active=True).first()

    if cart_product and (cart_product.quantity+quantity <= product.avail_quantity):
        cart_product.quantity += quantity
        cart_product.save()
        payload = {
            'result': True,
            'data': CartProductSerializer(instance=cart_product).data
        }
        return Response(payload)
    elif not cart_product and product.avail_quantity >= quantity:
        cart_product = CartProducts.objects.create(user=user, product=product, quantity=quantity)
        payload = {
            'result': True,
            'data': CartProductSerializer(instance=cart_product).data
        }
        return Response(payload)
    else:
        return Response({'result': False, 'message': AVAILABLE_QUANTITY + str(quantity)},
                        status=status.HTTP_400_BAD_REQUEST)


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
        return Response({'result': True, 'data': PRODUCT_REMOVED})
    else:
        return Response({'result': False, 'message': INVALID_PRODUCT_CART},
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
        return Response({'result': False, 'message': QUANTITY_NOT_AVAILABLE},
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
    :param customer_order_id: this will be the customer_order_id generated while ordering.
    :return: NONE
    """
    order = Orders.objects.filter(customer_order_id=customer_order_id).first()
    if order.is_subscription:
        pass
    else:
        body = ORDER_CONFIRMATION_EMAIL_BODY % (str(order.amount_payable), str(customer_order_id))
        cart_products = order.cartproducts_set.all()
        for product in cart_products:
            body += ORDER_CONFIRMATION_EMAIL_BODY_PRODUCTS % (
                product.product.name, str(product.quantity), str(product.quantity * product.product.cost))
        subject = ORDER_CONFIRMATION_EMAIL_SUBJECT
        send_text_email(body=body, subject=subject, to_address=order.user.email)


def initiate_payment(data):
    """
        This will update the payment details and initiate payment if necessary.
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
        return Response({'result': False, 'message': INITIATE_PAYMENT_VALIDATION},
                        status=status.HTTP_400_BAD_REQUEST)


def reset_product_quantities(order):
    """
        This will reset the quantities of product, upon order cancellation or bad paymment.
    :param order: the order instance.
    :return: None
    """
    cart_products = order.cartproducts_set.all()

    for product in cart_products:
        product.product.avail_quantity += product.quantity
        product.product.save()


def confirm_payment(data):
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
            Orders.objects.filter(customer_order_id=customer_order_id).update(amount_paid=amount_paid,
                                                                              payment_status=True,
                                                                              is_confirmed=True)
            send_mail_on_order_confirmation(customer_order_id)
        else:
            order = Orders.objects.filter(customer_order_id=customer_order_id).first()
            reset_product_quantities(order)

            order.payment_status = payment_status
            order.save()
        return Response({'result': True}, status=status.HTTP_200_OK)
    else:
        return Response({'result': False, 'message': PAYMENT_CONFIRMATION_VALIDATION},
                        status=status.HTTP_400_BAD_REQUEST)


def get_order_of_user(user):
    """
        This will fetch the order list of user.
    :param user: User fetched from request.
    :return: List of orders will be returned.
    """
    payload = {
        'result': True,
        'data': OrdersSerializers(instance=Orders.objects.filter(user=user), many=True).data
    }
    return Response(payload, status=status.HTTP_200_OK)


def cancel_order(user, order_id):
    """
        Any user can cancel his own order and admin can cancel any order.
    :param user: user fetched from request.
    :param order_id: Order that needs to be cancelled.
    :return: True or False, with appropriate response message.
    """
    try:
        order = Orders.objects.get(pk=order_id)
    except ObjectDoesNotExist:
        return Response({'result': False, 'message': INVALID_ORDER})

    if order.user == user or user.is_staff:
        reset_product_quantities(order)
        order.is_cancelled = True
        order.cancelled_by = user
        order.save()
        return Response({'result': True})
    else:
        return Response({'result': False, 'message': NOT_ALLOWED}, status=status.HTTP_403_FORBIDDEN)


def view_all_orders():
    """
        This will return the list of all the orders.
    :return:
    """
    payload = {
        'result': True,
        'data': OrdersSerializers(instance=Orders.objects.al(), many=True).data
    }

    return Response(payload, status=status.HTTP_200_OK)
