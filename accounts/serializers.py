from rest_framework import serializers
from accounts.models import MyUser


class MyUserSerializer(serializers.ModelSerializer):
    """
        This serializer is for fetching the user data.
    """
    class Meta:
        model = MyUser
        exclude = ('password', 'email_token', 'email_token_created_on', 'groups', 'user_permissions')


class MyUserSignupSerializer(serializers.ModelSerializer):
    """
        This is for data validation during the signup.
    """
    class Meta:
        model = MyUser
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number')
