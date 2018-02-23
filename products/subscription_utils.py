from datetime import date, timedelta, datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status

from products.constants import *
from products.models import Subscriptions, Products, Categories, Orders
from products.serializers import SubscriptionSerializer


def add_subscription(user, data):
    """
    :param user: User object to which the subscription has to be added.
    :param data: The data of the subscription to be added
    :return: Response whether the subscription was successfully added(status=200) or not(status=404).
    """
    if not user:
        return Response({'status': USER_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

    valid_fields = ['product_id', 'category_id', 'quantity']
    product_exists = False
    category_exist = False
    for element in data:
        if element == valid_fields[0]:
            product_exists = True
        elif element == valid_fields[1]:
            category_exist = True
        else:
            return Response({'status': INVALID_FIELDS},
                            status=status.HTTP_400_BAD_REQUEST)

    if not product_exists or not category_exist:
        return Response({'status': SUBSCRIPTION_FIELD_ERROR},
                        status=status.HTTP_400_BAD_REQUEST)

    # Check whether category option is available in product
    try:
        product = Products.objects.get(pk=data[valid_fields[0]], category_ids=data[valid_fields[1]])
    except ObjectDoesNotExist:
        return Response({'status': CATEGORY_NOT_FOR_PRODUCT},
                        status=status.HTTP_400_BAD_REQUEST)

    new_subscription = Subscriptions.objects.create(user=user, **data)
    new_subscription.save()
    return Response({'status': SUBSCRIPTION_ADDED}, status=status.HTTP_200_OK)


def view_subscription(pk):
    """
    :param pk: Primary key of user for whom the subscriptions are to be fetched.
    :return: Response with data having all subscriptions of the user
    """

    query = Subscriptions.objects.filter(user_id=pk)
    serializer = SubscriptionSerializer(query, many=True)
    return Response(serializer.data)


def finalize_subscription(subscription_id, data):
    """
    :param subscription_id: Subscription which is to be finalized.
    :param data: Data containing dates of order and payment details
    :return: Response whether the order was finalized or not.
    """
    try:
        sub = Subscriptions.objects.get(pk=subscription_id)
    except ObjectDoesNotExist:
        return Response({'status': SUBSCRIPTION_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)

    if sub.status == 'A':
        return Response({'status': SUBSCRIPTION_ACTIVE}, status=status.HTTP_400_BAD_REQUEST)

    if sub.product is None or sub.product.is_delete:
        return Response({'status': PRODUCT_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)

    date_format = "%d-%m-%Y"
    valid_fields = ['next_order_date', 'last_order_date', 'paid_till']
    for element in data:
        if element in valid_fields:
            setattr(sub, element, datetime.strptime(data[element], date_format))

    setattr(sub, 'status', 'A')
    setattr(sub, 'start_date', datetime.now())
    sub.save()

    return Response({'status': SUBSCRIPTION_FINALIZED}, status=status.HTTP_200_OK)


def get_days_from_category_id(key):
    """
    :param key: Primary Key of category
    :return: Integer containing number of days of periodicity
    """
    try:
        category = Categories.objects.get(pk=key)
    except ObjectDoesNotExist:
        return {'status': False}

    number_of_days = category.period_number
    multiplier = 1
    if category.period_name == 'week':
        multiplier = 7
    elif category.period_name == 'month':
        multiplier = 30

    number_of_days = number_of_days * multiplier
    return {'status': True, 'data': number_of_days}


def insert_into_order_from_subscription(subscription_id, payment_status, payment_type):

    """
    :param subscription_id: Primary Key of Subscription which is to be inserted
    :param payment_type: Payment type for the order
    :param payment_status: Payment status of the order
    :return: Successful or unsuccessful status depending on whether the order was placed
    """

    try:
        subscription = Subscriptions.objects.get(pk=subscription_id)
    except ObjectDoesNotExist:
        return {'status': SUBSCRIPTION_NOT_FOUND}

    try:
        product = Subscriptions.objects.get(pk=subscription_id).product
        if product.is_delete:
            return {'status': PRODUCT_NOT_FOUND}
    except ObjectDoesNotExist:
        return {'status': PRODUCT_NOT_FOUND}

    if product.avail_quantity < subscription.quantity:
        return {'status': 'False'}

    product.avail_quantity = product.avail_quantity - subscription.quantity
    product.save()

    if payment_status:
        cost_paid = product.cost
    else:
        cost_paid = 0

    new_order = Orders.objects.create(user_id=subscription.user_id, is_subscription=True,
                                      subscription_id=subscription_id, payment_type=payment_type,
                                      payment_status=payment_status)
    new_order.save()
    return {'status': 'True'}


def new_orders_from_subscription():
    """
    Places orders from subscriptions.
    :return: Checks and return the subscriptions which are to be ordered in the next 7 days.
    """
    today = date.today()
    next_week_subscriptions = Subscriptions.objects.filter(status='A').\
        filter(next_order_date__range=[today, today + timedelta(days=7)])

    shifted_subscriptions = []
    cancelled_subscriptions = []
    for obj in next_week_subscriptions:
        if obj.next_order_date > obj.last_order_date:
            setattr(obj, 'status', 'F')
        else:

            if obj.paid_till is None:
                payment_status = False
                payment_type = 'C'
            elif obj.paid_till >= obj.next_order_date:
                payment_status = True
                payment_type = 'N'
            else:
                payment_status = False
                payment_type = 'C'

            periodicity = get_days_from_category_id(obj.category_id)
            if periodicity['status']:
                result = insert_into_order_from_subscription(obj.id, payment_status, payment_type)

                if result['status'] == 'True':
                    # TODO Inform user of the order placed.
                    previous_order = obj.next_order_date
                    next_order_date = previous_order + timedelta(days=periodicity['data'])
                    if next_order_date > obj.last_order_date:
                        setattr(obj, 'status', 'F')
                    else:
                        setattr(obj, 'next_order_date', next_order_date)
                    obj.save()

                elif result['status'] == 'False':
                    # Here the quantity of the product is not available, so the subscription is automatically shifted,
                    # to the next date.
                    # TODO Inform user of the shifting of subscription due non-availability of product.
                    shifted_subscriptions.append(obj.id)
                    next_date = obj.next_order_date + timedelta(days=periodicity['data'])
                    next_date = next_date.strftime('%d-%m-%Y')
                    shift_subscription(obj.id, next_date)

                elif result['status'] == PRODUCT_NOT_FOUND:
                    # The product itself has been discontinued.
                    # TODO Inform user for the cancellation of the subscription due to removal of product.
                    cancelled_subscriptions.append(obj.id)
                    cancel_subscription(obj.id)

            else:
                # If and when the selected periodicity for a product is removed from the admin,
                # or is no longer provided by the merchant or so, then all the subscriptions
                # with that product and that periodicity will be cancelled.
                # TODO Inform user for the cancellation of the subscription due to removal of category option of that
                # TODO product.
                cancelled_subscriptions.append(obj.id)
                cancel_subscription(obj.id)

    serialized = SubscriptionSerializer(next_week_subscriptions, many=True)
    return Response({'cancelled': cancelled_subscriptions, 'shifted': shifted_subscriptions, 'data': serialized.data})


def shift_subscription(subscription_id, next_order_date):
    """
    :param subscription_id: Primary Key of subscription which is to be shifted
    :param next_order_date: The date to which the subscription is to be shifted
    :return: Response whether the subscription was successfully shifted(status=200) or not(status=400)
    """
    try:
        subscription = Subscriptions.objects.get(pk=subscription_id)
    except ObjectDoesNotExist:
        return Response({'status': SUBSCRIPTION_NOT_FOUND})

    date_format = '%d-%m-%Y'
    next_order_date = datetime.strptime(next_order_date, date_format)

    if datetime.now() + timedelta(days=1) > next_order_date:
        return Response({'status': SUBSCRIPTION_DATE_ERROR}, status=status.HTTP_400_BAD_REQUEST)

    if subscription.status != 'A':
        return Response({'status': SUBSCRIPTION_NOT_ACTIVE}, status=status.HTTP_400_BAD_REQUEST)

    setattr(subscription, 'last_order_date', next_order_date + timedelta(days=
            (subscription.last_order_date.date() - subscription.next_order_date.date()).days))

    if subscription.paid_till is not None:
        setattr(subscription, 'paid_till', subscription.paid_till + timedelta(days=
                (subscription.last_order_date.date() - subscription.next_order_date.date()).days))

    setattr(subscription, 'next_order_date', next_order_date)

    subscription.save()
    return Response({'status': SUBSCRIPTION_SHIFTED}, status=status.HTTP_200_OK)


def cancel_subscription(subscription_id):
    """
    :param subscription_id: Subscription's Primary Key which needs to be cancelled
    :return: Response whether the subscription was successfully cancelled or not
    """
    try:
        subscription = Subscriptions.objects.get(pk=subscription_id)
    except ObjectDoesNotExist:
        return Response({'status': SUBSCRIPTION_NOT_FOUND})

    if subscription.status == 'A':
        setattr(subscription, 'status', 'C')
        subscription.save()
        # Refund payment if paid_till was greater.
        return Response({'status': SUBSCRIPTION_CANCELLED}, status=status.HTTP_200_OK)
    return Response({'status': SUBSCRIPTION_NOT_ACTIVE}, status=status.HTTP_400_BAD_REQUEST)
