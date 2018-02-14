from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import MyUser

# Create your views here.


class SignUpView(APIView):
    """
        Signup for the user.
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
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
            # TODO send_email to verify email address
            pass
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({'result': True, 'message': 'User registered successfully.'})
