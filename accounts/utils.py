import requests
import datetime
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from accounts.models import MyUser
import coffee.settings as st


def register_user(user_type, query_data):
    """
        Helper function to register user.
    """
    if MyUser.objects.filter(email=query_data['email']):
        response = {'result': False, 'message': 'User already exists'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    if user_type == 'super_user':
        MyUser.objects.create_superuser(**query_data)
    elif user_type == 'user':
        user = MyUser.objects.create_user(**query_data)
        user.send_verification_email()
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response({'result': True, 'message': 'User registered successfully.'})


def get_auth_token(email, password):
    """
        This methods sends the post request to fetch the access and refresh token.
    """
    url = 'http://localhost:8000/o/token/'
    auth = (st.CLIENT_ID, st.CLIENT_SECRET)
    payload = {
        'grant_type': 'password',
        'username': email,
        'password': password
    }
    return requests.post(url, data=payload, auth=auth)


def login_user(email, password):
    """
        This will first confirm if user is already registered with email or not,
        if not then it wil send the email to verify the user.
    """
    user = MyUser.objects.filter(email=email).first()

    if user:
        if user.is_verified:
            response = get_auth_token(email, password)
            return Response(response.json())
        else:
            user.send_verification_email()
            return Response({'result': True, 'message': 'Verify Your Email First'})
    else:
        return Response({'result': False, 'message': 'Invalid Credentials'})


def check_within_time(original_date, time_period_allowed):
    """
    :param original_date: Time at which token was generated
    :param time_period_allowed: Link should be used in what period of time
    :return: True or False
    """
    checker_date = timezone.now() - datetime.timedelta(**time_period_allowed)

    if checker_date > original_date:
        return False

    return True


def verify_email(token):
    """
        This will help in verifying email.
    """
    user = MyUser.objects.filter(email_token=token).first()

    if user:
        if not check_within_time(user.email_token_created_on, {'days': 2}):
            response = HttpResponse("<h1>Link Expired</h1>")
        else:
            user.is_verified = True
            response = HttpResponse("<h1>Email Address Successfully Verified</h1>")

        user.email_token = ""
        user.save()

        return response

    return HttpResponse("<h1>Link Does not Exist </h1>")


def reset_password_form(token):
    """
        If the link is clicked within 2 days it will return password reset form.
    """
    user = MyUser.objects.filter(email_token=token).first()

    if user:
        if not check_within_time(user.email_token_created_on, {'days': 2}):
            response = HttpResponse("<h1>Link Expired</h1>")
        else:
            user.is_verified = True
            # TODO password reset form should be returned
            response = HttpResponse("<h1>You can verify your password</h1>")

        user.save()

        return response

    return HttpResponse("<h1>Link Does not Exist </h1>")


def reset_password(token, password):
    """
        It will help to reset the password, and also verifies email, if not verified.
    """
    user = MyUser.objects.filter(email_token=token).first()

    if user:
        if not check_within_time(user.email_token_created_on, {'days': 2}):
            response = {'result': False, 'message': 'Link expired.'}
            user.email_token = ""
        else:
            user.is_verified = True
            user.set_password(password)
            user.email_token = ""
            response = {'result': True, 'message': 'Password reset successful.'}

        user.save()

        return Response(response)

    return Response({'result': False, 'message': 'Link does not exists.'})
