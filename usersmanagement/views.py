from contextvars import Token
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import  LoginSerializer,ChangePasswordSerializer,resetPasswordRequestSerializer,resetPasswordSerializer,UserProfileSerializer,CustomUserSerializer,UserUpdateSerializer
from rest_framework import status
from django.contrib.auth import authenticate,login,update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import  check_password
from usersmanagement.models import CustomUser
import jwt
from datetime import datetime, timedelta
from .utils import send_password_reset_email
from django.contrib.auth.models import Group

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': 'This is a protected view. You have a valid JWT token.'}, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    """
    Log in with a username and password.

    To log in, send a POST request with the following JSON data:
    {
        "username": "your_username",
        "password": "your_password"
    }

    If the login is successful, you will receive an authentication token.
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # If authentication is successful, generate or retrieve an authentication token
                login(request, user)  # You can use login to persist the user's session if needed
                permissions=list(user.get_all_permissions())
                user_groups = user.groups.all()  # Get the groups associated with the user
                group_names = [group.name for group in user_groups]
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                return Response({'status': 'true', 'message': 'Login successful','access_token': access_token, 'refresh_token': refresh_token,
                                 "permissions":permissions,
                                 "groups":group_names,
                                 "username":user.username}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    Change the user's password by providing the username, old password, and new password.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the old password is correct
            if check_password(old_password, user.password):
                # Update the password and session auth hash
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Update the session's auth hash

                return Response({'status':True,'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid old password.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ResetPasswordRequestview(APIView):
    """
    Reset  user's password using username and email we will send out a email to the user with reset link.
    """ 
    def post(self,request):
        serializer=resetPasswordRequestSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            try:
               # check if the user exists with abov email and password 
               user=CustomUser.objects.get(email=email,username=username)
               email=user.email
               username=user.username
               # Generate a JWT token
               token_payload = {
                'user_id': username,
                'exp': datetime.utcnow() + timedelta(hours=24),  # Token expiration time
                }
               token = jwt.encode(token_payload, 'your_segdfgdfgdcret_key', algorithm='HS256')
               print(token)
               send_password_reset_email(username=username,email=email,link=f'http://localhost:3000/pages/resetPassword?token="{token}"&&username={username}')
               return Response({'status':True,'message':'Password email was sent'},status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'error':'User not found'},status=status.HTTP_404_NOT_FOUND)

        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
       

class ResetPasswordView(APIView):
    """
    Reset  user's password using token generated in password reset request.
    """ 
    def post(self,request):
        serializer=resetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            # Verify a JWT token
            try:
                decoded_token = jwt.decode(token, 'your_segdfgdfgdcret_key', algorithms=['HS256'])
                user = CustomUser.objects.get(username=username)
                # Update the password and session auth hash
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Update the session's auth hash

                return Response({'status':True,'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
              
            # Token is invalid
            except jwt.ExpiredSignatureError:
                return  Response({'message':'Link Expired'},status=status.HTTP_401_UNAUTHORIZED)
            # Token has expired
            except jwt.DecodeError:
                return  Response({'message':'Invalid link'},status=status.HTTP_401_UNAUTHORIZED)
            # Token is invalid (e.g., tampered with)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
       
class GetUserProfileDetails(APIView):
    """Fetch the user profile deatils based on the user name"""
    def get(self,request):
        username= {'username':request.GET.get('username')}
        serializer=UserProfileSerializer(data=username)
        if serializer.is_valid():
            try:

                user=CustomUser.objects.get(username=username['username'])
                serializer = CustomUserSerializer(user)
                return Response({'status':True,'userDetails':serializer.data}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'error':'User not found'},status=status.HTTP_404_NOT_FOUND)

        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



class UpdateUserProfile(APIView):
    """ Update user first and last name"""
    def post(self,request):
        username = request.data.get('username')  # Change 'username' to the appropriate field
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Proceed with the update if the user exists
        serializer = UserUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'status':True,'message': 'Profile Updated.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        