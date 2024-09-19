
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

from user.pormissions import IsProfessionalUser
from .serializers import *
from .models import *
from django.shortcuts import render
from rest_framework.generics import GenericAPIView, UpdateAPIView,RetrieveAPIView, CreateAPIView,DestroyAPIView
from user.utils import send_code_to_user
from rest_framework.response import Response
from rest_framework import status , generics
from rest_framework.permissions import IsAuthenticated
from .utils import OneTimePassword
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()

class CityCreateListView(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class AddressCreateListView(generics.ListCreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer
    
    def post(self, request):
        user_data=request.data
        serializer=self.serializer_class(data = user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user=serializer.data
            send_code_to_user(user['email'])
            # send email function user['email']
            return Response({
                'data':user,
                'message':f"hi {user['first_name']} thanks for signing up a passcode has be sent to your email"
                
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        otpcode =request.data.get('otp')
        try:
            user_code_obj = OneTimePassword.objects.get(code = otpcode)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({
                    'message':'account email verified successfullly'
                }, status=status.HTTP_200_OK)
            return Response({
                'message':'code is invalid user already verified'
            }, status = status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist:
            return Response({
                'message':'passcode not provided'
            }, status=status.HTTP_404_NOT_FOUND)
            
            

class LoginUserView(GenericAPIView):
    serializer_class=LoginSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class UserProfileRegister(GenericAPIView):
    


class TestAuthenticationView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        data = {
            'user': serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)

class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'a link has been sent to your email to reset password'},status=status.HTTP_200_OK)
    
class PasswordResetConfirm(GenericAPIView):
    def get(self,request,uidb64,token):
        try:
            user_id =smart_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                return Response({'message':'token is invalid ot has expired'},status=status.HTTP_401_UNAUTHORIZED),
            return Response({'success':True,'message':'credentials is valid', 'uidb64': uidb64, 'token':token},status=status.HTTP_200_OK)
        
        except DjangoUnicodeDecodeError:
            
            return Response({'message':'token is invalid ot has expired'},status=status.HTTP_401_UNAUTHORIZED),


class SetNewPassword(GenericAPIView):
    serializer_class=SetNewPasswordSerializer
    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message':'password reset successfull'}, status=status.HTTP_200_OK)
    


class UserProfileImageView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileImageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the current authenticated user
        return self.request.user

# USER ADDRESS CREATE AND LIST VIEW---------------------->


class UserAddressListCreateView(generics.ListCreateAPIView):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError("This address already exists for the user.")

#  USER ADDRESS DELETE VIEW
class UserAddressDeleteView(generics.DestroyAPIView):
    queryset = UserAddress.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only delete their own addresses
        return super().get_queryset().filter(user=self.request.user)

# UPDATE USER EMIAL VIEW-------------------------------------->
class UserEmailUpdateView(generics.CreateAPIView):
    queryset = EmailUpdateCode.objects.all()
    serializer_class = UserEmailUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

# VERIFY UPDATE USER EMIAL VIEW-------------------------------->

class UserEmailVerifyUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        otpcode = request.data.get('otp')
        try:
            user_code_obj = EmailUpdateCode.objects.get(code=otpcode)
            user = user_code_obj.user
            user.email = user_code_obj.email  # Update user's email
            user.save()
            return Response({
                'message': 'Email Updated successfully'
            }, status=status.HTTP_200_OK)
           
        except EmailUpdateCode.DoesNotExist:
            return Response({
                'message': 'Code is invalid'
            }, status=status.HTTP_404_NOT_FOUND)
        

# USER CHANGE PASSWORD VIEW-------------------------------->

class UpdatePasswordView(generics.UpdateAPIView):
    serializer_class = UpdatePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
# --------------------------------------  PROFESSIONAL VIEWS ----------------------------------------------

# CREATE PROFESSIONAL VIEW -------------------------------->

class ProfessionalListCreateView(generics.ListCreateAPIView):
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Optionally filter by the current user
        return Professional.objects.filter(admin=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the admin field to the logged-in user
        serializer.save(admin=self.request.user)

# UPDATE RETRIVE AND DELETE PORFESSION VIEWS------------------>

class ProfessionalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfessionalSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get the Professional instance associated with the authenticated user
        return Professional.objects.get(admin=self.request.user)
    
# CREATE PROFESSION SERVICE VIEW----------------->
class ProfessionalServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ProfessionalServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter services by the current professional
        return ProfessionalService.objects.filter(professional=self.request.user.professional)

class ProfessionalServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfessionalServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter services by the current professional
        return ProfessionalService.objects.filter(professional=self.request.user.professional)



class SomeProfessionalView(APIView):
    permission_classes = [IsAuthenticated, IsProfessionalUser]

    def get(self, request):
        # Check if the user is a professional
        if IsProfessionalUser().has_permission(request, self):
            return Response({"isProfessional": True}, status=200)
        else:
            return Response({"isProfessional": False}, status=403)
        


class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        # Try to get the first address associated with the user, or None if not found
        user_address = UserAddress.objects.filter(user=user).first()

        if not user_address:
            data = {
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'last_login': user.last_login,
                    'profile_image': user.profile_image.url if user.profile_image else None,
                    'phone': user.phone,
                },
                'address': None  # Set address to None
            }
            return Response(data, status=status.HTTP_200_OK)

        # Serialize the user address
        serializer = UserProfileSerializer(user_address)
        return Response(serializer.data, status=status.HTTP_200_OK)