from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from accounts.utils import verify_email, register_user, login_user, revoke_auth_token, reset_password_form,\
    reset_password

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
        user_type = request.data['user_type']
        return register_user(user_type, request.data)


class VerifyEmailView(APIView):
    """
        This will verify the email.
    """
    permission_classes = ()

    def get(self, request, token):
        """
            Check if the email got verified within 2 days.
        """
        return verify_email(token)


class ResetPasswordView(APIView):
    """
        This will reset the password
    """
    permission_classes = ()

    def get(self, request, token):
        """
            Won't let user to rest the password after 2 days and 2nd time.
        """
        return reset_password_form(token)

    def post(self, request, token):
        """
            Let the user change the password for the first time within 2 days
        """
        _password = request.data['password']
        _confirmed_password = request.data['confirm_password']

        if _password == _confirmed_password:
            return reset_password(token, _password)

        return Response({'result': False, 'message': "Password doesn't match"})


class LoginView(APIView):
    """
        This will help in login using OAuth2.
    """
    permission_classes = ()

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        return login_user(email, password)


class LogoutView(APIView):
    """
        This will help in logout of user.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        token = request.auth
        return revoke_auth_token(token)
