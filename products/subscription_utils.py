from datetime import date, timedelta

from rest_framework.response import Response
from rest_framework import status

from products.serializers import SubscriptionSerializer
from products.models import Subscriptions, Products, Categories


def add_subscription(user, data):
    """
    :param user: User object to which the subscription has to be added.
    :param data: The data of the subscription to be added
    :return: Response whether the subscription was successfully added(status=200) or not(status=404).
    """
    if not user:
        return Response({'STATUS': 'USER NOT FOUND'}, status=status.HTTP_404_NOT_FOUND)

    valid_fields = ['product_id', 'category_id', 'quantity']
    product_exists = False
    category_exist = False
    for element in data:
        if element == valid_fields[0]:
            product_exists = True
        elif element == valid_fields[1]:
            category_exist = True
        else:
            return Response({'STATUS': 'INVALID_DATA'}, status=status.HTTP_400_BAD_REQUEST)

    if not product_exists or not category_exist:
        return Response({'STATUS': 'INVALID DATA'}, status=status.HTTP_400_BAD_REQUEST)

    # Check whether category option is available in product
    product = Products.objects.filter(pk=data[valid_fields[0]], category_ids=data[valid_fields[1]]).first()
    if not product:
        return Response({'STATUS': 'INVALID CATEGORY OPTION'}, status=status.HTTP_400_BAD_REQUEST)

    new_subscription = Subscriptions.objects.create(user=user, **data)
    new_subscription.save()
    return Response({'STATUS': 'SUBSCRIPTION SAVED'}, status=status.HTTP_200_OK)


def view_subscription(pk):
    """
    :param pk: Primary key of user for whom the subscriptions are to be fetched.
    :return: Response with data having all subscriptions of the user
    """
    query = Subscriptions.objects.filter(user_id=pk)
    serializer = SubscriptionSerializer(query, many=True)
    return Response(serializer.data)


def finalize_subscription(user, subscription_id, data):
    """
    :param user:  User object to which the subscription has to be finalized.
    :param subscription_id: Subscription which is to be finalized.
    :param data: Data containing dates of order and payment details
    :return: Response whether the order was finalized or not.
    """
    sub = Subscriptions.objects.filter(user=user, pk=subscription_id)
    valid_fields = ['start_date', 'next_order_date', 'last_order_date', 'paid_till']
    for element in data:
        if data in valid_fields:
            setattr(sub, element, data[element])
    return Response({'STATUS': 'SUBSCRIPTION FINALIZED'}, status=status.HTTP_200_OK)


def check_for_new_orders():
    """
    :return: Checks and return the subscriptions which are to be ordered in the next 7 days.
    """
    today = date.today()
    all_subscriptions = Subscriptions.objects.filter(status='A').\
        filter(next_order_date__range=[today, today + timedelta(days=7)])

    serialized = SubscriptionSerializer(all_subscriptions, many=True)
    return Response(serialized.data)
