from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import MyUser
import datetime
from django.utils import timezone
from django.http import HttpResponse

# Create your views here.


class SignUpView(APIView):
    """
        Signup for the user.
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        """
        It is used for creating users, not necessarily the super user.
        :param request: requires email, password, first_name, last_name, phone_number, user_type.
        :return: result = True with 200 response code.
        """
        query_data = dict()
        query_data['email'] = request.data['email']
        query_data['password'] = request.data['password']
        query_data['first_name'] = request.data['first_name']
        query_data['last_name'] = request.data['last_name']
        query_data['phone_number'] = request.data['phone_number']
        user_type = request.data['user_type']

        if MyUser.objects.filter(email=query_data['email']):
            response = {'result': False, 'message': 'User already exists'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if user_type == 'super_user':
            user = MyUser.objects.create_superuser(**query_data)
        elif user_type == 'user':
            user = MyUser.objects.create_user(**query_data)
            user.send_verification_email()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({'result': True, 'message': 'User registered successfully.'})


class VerifyEmailView(APIView):
    """
        This will verify the email.
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, token):
        """
            Check if the email got verified within 2 days.
        """
        user = MyUser.objects.filter(email_token=token).first()
        if user:
            checker_date = timezone.now() - datetime.timedelta(days=2)

            if checker_date > user.email_token_created_on:
                response = HttpResponse("<h1>Link Expired</h1>")
            else:
                user.is_verified = True
                response = HttpResponse("<h1>Email Address Successfully Verified</h1>")

            user.email_token = ""
            user.save()

            return response

        return HttpResponse("<h1>Link Does not Exist </h1>")
