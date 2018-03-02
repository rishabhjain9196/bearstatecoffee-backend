from datetime import date, timedelta, datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status

from accounts.utils import send_text_email
from products.constants import *
from products.models import Subscriptions, Products, Categories, Orders
from products.serializers import SubscriptionSerializer


def add_subscription(user, data):
    """
    :param user: User object to which the subscription has to be added.
    :param data: The data of the subscription to be added
    :return: Response whether the subscription was successfully added(status=200) or not(status=404).
    """

    valid_fields = ['product_id', 'category_id', 'quantity']
    product_id = data.get('product_id')
    category_id = data.get('category_id')

    # validating exact fields as in list valid_fields
    if not (all(keys in valid_fields for keys in data) and all(keys in data for keys in valid_fields)):
        return Response({'status': INVALID_FIELDS}, status=status.HTTP_400_BAD_REQUEST)

    # Check whether category option is available in product
    try:
        product = Products.objects.get(pk=product_id, category_ids=category_id, is_delete=False)
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


def finalize_subscription(user_id, subscription_id, data):
    """
    :param user_id: Primary key of user wanting to finalize subscription
    :param subscription_id: Subscription which is to be finalized.
    :param data: Data containing dates of order and payment details
    :return: Response whether the order was finalized or not.
    """
    try:
        sub = Subscriptions.objects.get(pk=subscription_id, user_id=user_id)
    except ObjectDoesNotExist:
        return Response({'status': SUBSCRIPTION_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)

    if sub.status == 'A':
        return Response({'status': SUBSCRIPTION_ACTIVE}, status=status.HTTP_400_BAD_REQUEST)

    if sub.product is None or sub.product.is_delete:
        return Response({'status': PRODUCT_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)

    date_format = "%d-%m-%Y"
    valid_fields = ['next_order_date', 'last_order_date']

    for element in data:
        if element in valid_fields:
            try:
                check_date = datetime.strptime(data[element], date_format)
            except ValueError:
                return Response({'status': INVALID_DATE}, status=status.HTTP_400_BAD_REQUEST)

            setattr(sub, element, check_date)
        else:
            return Response({'status': INVALID_FIELDS}, status=status.HTTP_400_BAD_REQUEST)

    if sub.next_order_date >= sub.last_order_date:
        return Response({'status': INVALID_DATE}, status=status.HTTP_400_BAD_REQUEST)

    paid_till = data.get('paid_till', None)
    if paid_till is not None:
        setattr(sub, 'paid_till', datetime.strptime(data['paid_till'], date_format))

    setattr(sub, 'status', 'A')
    setattr(sub, 'start_date', datetime.now())
    sub.save()

    return Response({'status': SUBSCRIPTION_FINALIZED}, status=status.HTTP_200_OK)


def get_days_from_category_id(category_id, product_id):
    """
    :param category_id: Primary Key of category
    :param product_id: Primary key of product
    :return: Integer containing number of days of periodicity
    """
    try:
        categories = Products.objects.get(pk=product_id).catergory_ids.all()
        category = Categories.objects.get(pk=category_id)
        if category not in categories:
            return {'status': False}
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
    amount_payable = product.cost * subscription.quantity

    if payment_status:
        amount_paid = amount_payable
    else:
        amount_paid = 0.00

    new_order = Orders.objects.create(user_id=subscription.user_id, is_subscription=True,
                                      subscription_id=subscription_id, payment_type=payment_type,
                                      payment_status=payment_status, is_confirmed=True, amount_payable=amount_payable,
                                      amount_paid=amount_paid)
    new_order.save()
    body = ORDER_CONFIRMATION_EMAIL_BODY % (str(amount_payable), str(new_order.customer_order_id))
    body += ORDER_CONFIRMATION_EMAIL_BODY_PRODUCTS % (str(product.name), str(subscription.quantity),
                                                      str(subscription.quantity * product.cost))
    subject = ORDER_CONFIRMATION_EMAIL_SUBJECT
    send_text_email(body=body, subject=subject, to_address=subscription.user.email)

    return {'status': 'True'}


def new_orders_from_subscription():
    """
    Places orders from subscriptions.
    :return: Checks and return the subscriptions which are to be ordered in the next 7 days.
    """
    today = datetime.today()
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

            periodicity = get_days_from_category_id(obj.category_id, obj.product_id)
            if periodicity['status']:
                result = insert_into_order_from_subscription(obj.id, payment_status, payment_type)

                if result['status'] == 'True':

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
                    shifted_subscriptions.append(obj.id)
                    next_date = obj.next_order_date + timedelta(days=periodicity['data'])
                    next_date = next_date.strftime('%d-%m-%Y')
                    shift_subscription(obj.id, next_date, reason=SHIFTING_REASON_NO_QUANTITY)

                elif result['status'] == PRODUCT_NOT_FOUND:
                    # The product itself has been discontinued.
                    cancelled_subscriptions.append(obj.id)
                    cancel_subscription(obj.id, reason=CANCEL_REASON_NO_PRODUCT)

            else:
                # If and when the selected periodicity for a product is removed from the admin,
                # or is no longer provided by the merchant or so, then all the subscriptions
                # with that product and that periodicity will be cancelled.
                cancelled_subscriptions.append(obj.id)
                cancel_subscription(obj.id, reason=CANCEL_REASON_NO_PERIOD)

    serialized = SubscriptionSerializer(next_week_subscriptions, many=True)
    return Response({'cancelled': cancelled_subscriptions, 'shifted': shifted_subscriptions, 'data': serialized.data})


def shift_subscription(user_id, subscription_id, next_order_date, reason=None):
    """
    :param user_id: Primary key of user
    :param subscription_id: Primary Key of subscription which is to be shifted
    :param next_order_date: The date to which the subscription is to be shifted
    :param reason: To provide a reason why the order was shifted.
    :return: Response whether the subscription was successfully shifted(status=200) or not(status=400)
    """
    try:
        subscription = Subscriptions.objects.get(pk=subscription_id, user_id=user_id)
    except ObjectDoesNotExist:
        return Response({'status': SUBSCRIPTION_NOT_FOUND})

    date_format = '%d-%m-%Y'
    string_date = next_order_date
    try:
        next_order_date = datetime.strptime(next_order_date, date_format)
    except ValueError:
        return Response({'status': INVALID_DATE}, status=status.HTTP_400_BAD_REQUEST)

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
    body = SUBSCRIPTION_SHIFT_BODY % (str(subscription.product.name), string_date)
    if reason is not None:
        body += reason
    subject = SUBSCRIPTION_SHIFT_SUBJECT
    send_text_email(body=body, subject=subject, to_address=subscription.user.email)

    return Response({'status': SUBSCRIPTION_SHIFTED}, status=status.HTTP_200_OK)


def cancel_subscription(user_id, subscription_id, reason=None):
    """
    :param user_id: Primary key of user
    :param subscription_id: Subscription's Primary Key which needs to be cancelled
    :param reason: To provide a reason why the order was cancelled.
    :return: Response whether the subscription was successfully cancelled or not
    """
    try:
        subscription = Subscriptions.objects.get(pk=subscription_id, user_id=user_id)
    except ObjectDoesNotExist:
        return Response({'status': SUBSCRIPTION_NOT_FOUND})

    if subscription.status == 'A':
        setattr(subscription, 'status', 'C')
        subscription.save()

        # TODO: Handle Refunds if paid_till was greater.

        body = SUBSCRIPTION_CANCEL_BODY % (str(subscription.product.name))
        if reason is not None:
            body += reason
        subject = SUBSCRIPTION_CANCEL_SUBJECT
        send_text_email(body=body, subject=subject, to_address=subscription.user.email)
        return Response({'status': SUBSCRIPTION_CANCELLED}, status=status.HTTP_200_OK)

    return Response({'status': SUBSCRIPTION_NOT_ACTIVE}, status=status.HTTP_400_BAD_REQUEST)
