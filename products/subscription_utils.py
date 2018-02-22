from datetime import date, timedelta, datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status

from products.serializers import SubscriptionSerializer
from products.models import Subscriptions, Products, Categories, Orders


def add_subscription(user, data):
    """
    :param user: User object to which the subscription has to be added.
    :param data: The data of the subscription to be added
    :return: Response whether the subscription was successfully added(status=200) or not(status=404).
    """
    if not user:
        return Response({'status': 'The user does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    valid_fields = ['product_id', 'category_id', 'quantity']
    product_exists = False
    category_exist = False
    for element in data:
        if element == valid_fields[0]:
            product_exists = True
        elif element == valid_fields[1]:
            category_exist = True
        else:
            return Response({'status': 'Invalid fields are passed to add subscription'},
                            status=status.HTTP_400_BAD_REQUEST)

    if not product_exists or not category_exist:
        return Response({'status': 'Product and Category are required fields to add a subscription'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Check whether category option is available in product
    try:
        product = Products.objects.get(pk=data[valid_fields[0]], category_ids=data[valid_fields[1]])
    except ObjectDoesNotExist:
        return Response({'status': 'The selected category is not available for this product.'},
                        status=status.HTTP_400_BAD_REQUEST)

    new_subscription = Subscriptions.objects.create(user=user, **data)
    new_subscription.save()
    return Response({'status': 'The subscription was successfully added.'}, status=status.HTTP_200_OK)


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
        return Response({'status': 'This subscription does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    if sub.status == 'A':
        return Response({'status': 'This subscription is already active.'}, status=status.HTTP_400_BAD_REQUEST)

    date_format = "%d-%m-%Y"
    valid_fields = ['next_order_date', 'last_order_date', 'paid_till']
    for element in data:
        if element in valid_fields:
            setattr(sub, element, datetime.strptime(data[element], date_format))

    setattr(sub, 'status', 'A')
    setattr(sub, 'start_date', datetime.now())
    sub.save()

    return Response({'status': 'This subscription has been successfully finalized.'}, status=status.HTTP_200_OK)


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
        return {'status': False}
    new_order = Orders.objects.create(user_id=subscription.user_id, is_subscription=True,
                                      subscription_id=subscription_id, payment_type=payment_type,
                                      payment_status=payment_status)
    new_order.save()
    return {'status': True}


def new_orders_from_subscription():
    """
    Places orders from subscriptions.
    :return: Checks and return the subscriptions which are to be ordered in the next 7 days.
    """
    today = date.today()
    next_week_subscriptions = Subscriptions.objects.filter(status='A').\
        filter(next_order_date__range=[today, today + timedelta(days=7)])

    for obj in next_week_subscriptions:
        if obj.next_order_date > obj.last_order_date:
            setattr(obj, 'status', 'F')
        else:

            if obj.paid_till >= obj.next_order_date:
                payment_status = True
                payment_type = 'N'
            else:
                payment_status = False
                payment_type = 'C'

            result = insert_into_order_from_subscription(obj.id, payment_status, payment_type)
            if result['status']:
                previous_order = obj.next_order_date
                periodicity = get_days_from_category_id(obj.category_id)
                if periodicity['status']:
                    next_order_date = previous_order + timedelta(days=periodicity['data'])

                    if next_order_date > obj.last_order_date:
                        setattr(obj, 'status', 'F')
                    else:
                        setattr(obj, 'next_order_date', next_order_date)

        obj.save()

    serialized = SubscriptionSerializer(next_week_subscriptions, many=True)
    return Response(serialized.data)


def shift_subscription(subscription_id, next_order_date):
    """
    :param subscription_id: Primary Key of subscription which is to be shifted
    :param next_order_date: The date to which the subscription is to be shifted
    :return: Response whether the subscription was successfully shifted(status=200) or not(status=400)
    """
    try:
        subscription = Subscriptions.objects.get(pk=subscription_id)
    except ObjectDoesNotExist:
        return Response({'status': 'This subscription does not exist. '})

    date_format = "%d-%m-%Y"
    next_order_date = datetime.strptime(next_order_date, date_format)

    if datetime.now() + timedelta(days=1) > next_order_date:
        return Response({'status': 'The new order date has to be at least 1 day ahead of today.'},
                        status=status.HTTP_400_BAD_REQUEST)

    if subscription.status != 'A':
        return Response({'status': 'This subscription is not currently active.'},
                        status=status.HTTP_400_BAD_REQUEST)

    setattr(subscription, 'last_order_date', next_order_date + timedelta(days=
            (subscription.last_order_date.date() - subscription.next_order_date.date()).days))
    setattr(subscription, 'paid_till', subscription.paid_till + timedelta(days=
            (subscription.last_order_date.date() - subscription.next_order_date.date()).days))
    setattr(subscription, 'next_order_date', next_order_date)

    subscription.save()
    return Response({'status': 'The subscription was successfully shifted.'}, status=status.HTTP_200_OK)


def cancel_subscription(subscription_id):
    """
    :param subscription_id: Subscription's Primary Key which needs to be cancelled
    :return: Response whether the subscription was successfully cancelled or not
    """
    try:
        subscription = Subscriptions.objects.get(pk=subscription_id)
    except ObjectDoesNotExist:
        return Response({'status': 'This subscription does not exist.'})

    if subscription.status == 'A':
        setattr(subscription, 'status', 'C')
        subscription.save()
        return Response({'status': 'The subscription has been cancelled.'}, status=status.HTTP_200_OK)
    return Response({'status': 'The subscription cannot be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)