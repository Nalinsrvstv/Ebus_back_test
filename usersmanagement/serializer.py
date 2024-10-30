from rest_framework import serializers
from django.core import validators
from .models import CustomUser

class ChangePasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[
            validators.MinLengthValidator(limit_value=8, message="Password must be at least 8 characters long."),
            validators.RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).+$',
                message="Password must include at least one uppercase letter,  one digit, and one special character."
            ),
        ]
    )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class resetPasswordRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True,validators=[
        validators.EmailValidator()
    ])

class resetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    token=serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[
            validators.MinLengthValidator(limit_value=8, message="Password must be at least 8 characters long."),
            validators.RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).+$',
                message="Password must include at least one uppercase letter,  one digit, and one special character."
            ),
        ]
    )



class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
   
class CustomUserSerializer(serializers.ModelSerializer):
    # Define a formatted date_joined field
    formatted_date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", source="date_joined")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name','last_name','formatted_date_joined','groups')





class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name')