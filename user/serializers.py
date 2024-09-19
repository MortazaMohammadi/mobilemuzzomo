<<<<<<< HEAD
from django.core.mail import EmailMessage

from django.contrib.auth.hashers import make_password

from MuzzomoBackend import settings
from .models import *
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django .contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_bytes, force_str
from django.urls import reverse
from .utils import generateOtp, send_normal_email
from django.contrib.auth.password_validation import validate_password

# ADDRESS SERIALIZER--------------------------------->

# Serializer for Province
class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['name', 'code']

# Serializer for City with province code as prefix
class CitySerializer(serializers.ModelSerializer):
    province_code = serializers.CharField(source='province.code', read_only=True)

    class Meta:
        model = City
        fields = ['name', 'province_code']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Customize the output to be "CityName, ProvinceCode" (e.g., "Toronto, ON")
        representation['city_with_province'] = f"{representation['name']}, {representation['province_code']}"
        return representation

# Serializer for Address with full address representation
class AddressSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    province_code = serializers.CharField(source='city.province.code', read_only=True)

    class Meta:
        model = Address
        fields = ['unit_suite', 'street', 'city_name', 'province_code']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Customize the output to be "unit, street, city, province code" (e.g., "Unit 3, 123 Main St, Toronto, ON")
        representation['full_address'] = f"{representation['unit_suite']}, {representation['street']}, {representation['city_name']}, {representation['province_code']}"
        return representation

# --------------------------------------------------------------------------------------------------------------------------------


# USER REGISTERATION SERIALIZER--------------------------------->
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField( write_only = True, validators=[validate_password])
    password2 = serializers.CharField( write_only = True)
    
    class  Meta:
        model = User
        fields=['email', 'first_name', 'last_name', 'password','password2']
        
    def validate(self, attrs):
        password = attrs.get('password','')
        password2 = attrs.get('password2','')
        if password != password2:
            raise serializers.ValidationError('passwords do not match')
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            first_name = validated_data.get('first_name'),
            last_name = validated_data.get('last_name'),
            password = validated_data.get('password'),

        )
        return user
            
# LOGIN SERIALIZER--------------------------------->
class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length = 255, min_length=6)
    password = serializers.CharField(validators=[validate_password], write_only=True)
    full_name = serializers.CharField(max_length=255,read_only=True)
    access_token = serializers.CharField(max_length = 255, read_only = True)
    refresh_token = serializers.CharField(max_length = 255, read_only = True)
    
    class Meta:
        model = User
        fields=['email','password','full_name', 'refresh_token', 'access_token']
        
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        print(email)
        print(password)
        request=self.context.get('request')
        user = authenticate(request, email = email, password = password)
        if not user:
            raise AuthenticationFailed('invalid credintials try again')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        user_tokens = user.tokens()
        
        return{
            'email':user.email,
            'full_name':user.get_full_name,
            'access_token' : str(user_tokens.get('access')),
            'refresh_token':str(user_tokens.get('refresh'))
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'profile_image','last_login']

    profile_image = serializers.SerializerMethodField()

    def get_profile_image(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None
    
    
class UserPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone']

    def update(self, instance, validated_data):
        # Get the new phone number
        phone = validated_data.get('phone', None)
        
        if phone:
            # Update the phone field
            instance.phone = phone
            instance.save()
        
        return instance

# RESET PASSWORD SERIALIZER---------------------------------> 
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    
    class  Meta:
       fields=['email']
       
    def validate(self,attrs):
        email=attrs.get('email')
        if User.objects.filter(email = email):
            user = User.objects.get(email = email)
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request=self.context.get('request')
            site_domain=get_current_site(request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64':uidb64, 'token':token})
            abslink=f"http://{site_domain}{relative_link}"
            email_body=f"Hi use the link below to reset your password \n {abslink}"
            data={
                'email_body':email_body,
                'email_subject':'Reset Your Password',
                'to_email':user.email
            }
            send_normal_email(data)
            
        return super().validate(attrs)

# SET NEW PASSWORD SERIALIZER--------------------------------->
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6,write_only=True)
    confirm_password=serializers.CharField(max_length=100,min_length=6,write_only=True)
    uidb64=serializers.CharField(write_only=True)
    token=serializers.CharField(write_only=True)
    
    class Meta:
        fields=['password',
                'confirm_password',
                'uidb64',
                'token']
    def validate(self, attrs):
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            password = attrs.get('password')
            confirm_password=attrs.get('confirm_password')
            
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('reset link is invalid or has expired')
            if password != confirm_password:
                raise AuthenticationFailed("passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed('link is invalid or expired')

# USER PROFILE REGISTER SERIALIZER---------------------->

class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image']

    def update(self, instance, validated_data):
        # Get the new profile image
        profile_image = validated_data.get('profile_image', None)
        
        if profile_image:
            # If the instance already has a profile image, delete it
            if instance.profile_image:
                instance.profile_image.delete(save=False)
            
            # Update the profile image field
            instance.profile_image = profile_image
            instance.save()
        
        return instance
    
# USER ADDRESSES------------------------------------------>
class UserAddressSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = UserAddress
        fields = ['id', 'address']

    def validate(self, data):
        user = self.context['request'].user
        address_data = data.get('address')

        if address_data is None:
            raise serializers.ValidationError("Address data is required.")

        address_id = address_data.get('id')

        # Check if an address already exists for this user
        if address_id and UserAddress.objects.filter(user=user, address_id=address_id).exists():
            raise serializers.ValidationError("This address already exists for the user.")
        
        return data

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address, created = Address.objects.get_or_create(**address_data)
        user_address = UserAddress.objects.create(address=address, **validated_data)
        return user_address
    
# USER EMAIL UPDATE------------------------------------->

class UserEmailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUpdateCode
        fields = ['email']
    
    def create(self, validated_data):
        myuser = self.context['request'].user
        
        EmailUpdateCode.objects.filter(user=myuser).delete()
        # Send the OTP to the user's email
        Subject = "Ont Time passcode for Email verification"
        otpcode = generateOtp()
        email_body =f"HI {myuser.first_name} \n please verify your email with the \n one time passcode {otpcode}"
        from_email = settings.DEFAULT_FROM_EMAIL 

        d_email = EmailMessage(subject=Subject, body =email_body, from_email=from_email, to=(validated_data.get('email'),))
        d_email.send(fail_silently=True)

        emailUpdate = EmailUpdateCode.objects.create(
            user =  myuser,
            email = validated_data.get('email'),
            code = otpcode
        )
        return emailUpdate

class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        # Check if the old password is correct
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect"})

        # Ensure new password and confirm password match
        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "New password and confirm password do not match"})

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
# PROFESSIONAL SERIALIZERS-------------------------------->
class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ['id', 'license_number', 'insurance_number']
    
    def create(self, validated_data):
        # Get the current user from the request context
        user = self.context['request'].user
        
        # Check if a Professional with the same license_number already exists for this user
        if Professional.objects.filter(license_number=validated_data['license_number']).exists():
            raise serializers.ValidationError("A professional with this license number is already registered.")
        if Professional.objects.filter(insurance_number=validated_data['insurance_number']).exists():
            raise serializers.ValidationError("A professional with this license number is already registered.")
        if Professional.objects.filter(admin=user).exists():
            raise serializers.ValidationError("A professional with this license number is already registered.")
        # If no such Professional exists, create a new one
        validated_data['admin'] = user
        return Professional.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.license_number = validated_data.get('license_number', instance.license_number)
        instance.insurance_number = validated_data.get('insurance_number', instance.insurance_number)
        instance.save()
        return instance

# PROFESSIONAL SERVICES SERIALIZERS

class ProfessionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalService
        fields = ['id', 'serviceCatagory', 'serivce']

    def validate(self, data):
        # Get the current user as the professional
        professional = self.context['request'].user.professional

        # Check if the combination of professional and service already exists
        if ProfessionalService.objects.filter(
            professional=professional,
            service=data['serivce'],
            serviceCatagory=data['serviceCatagory']
        ).exists():
            raise serializers.ValidationError("This service is already registered for the professional.")

        return data

    def create(self, validated_data):
        # Set the professional field to the current user
        validated_data['professional'] = self.context['request'].user.professional
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Set the professional field to the current user
        validated_data['professional'] = self.context['request'].user.professional
        return super().update(instance, validated_data)
    

    # profile view


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code']

class ProvinceSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Province
        fields = ['id', 'name', 'code', 'country']

class CitySerializer(serializers.ModelSerializer):
    province = ProvinceSerializer(read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'province']

class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)

    class Meta:
        model = Address
        fields = ['id', 'street', 'unit_suite', 'city']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True, required=False)

    class Meta:
        model = UserAddress
=======
from django.core.mail import EmailMessage

from django.contrib.auth.hashers import make_password

from MuzzomoBackend import settings
from .models import *
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django .contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_bytes, force_str
from django.urls import reverse
from .utils import generateOtp, send_normal_email
from django.contrib.auth.password_validation import validate_password

# ADDRESS SERIALIZER--------------------------------->
class CountrySerializer(serializers.ModelSerializer):
  class Meta:
    model = Country
    fields = ['id' , 'name']
class ProvinceSerializer(serializers.ModelSerializer):
  class Meta:
    model = Province
    fields = ['id' , 'name' , 'country']
class CitySerializer(serializers.ModelSerializer):
  class Meta:
    model = City
    fields = ['id' , 'name' , 'province']
class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)

    class Meta:
        model = Address
        fields = ['id', 'street', 'unit_suite', 'city']

    # Overriding to accept writable city ID
    def to_internal_value(self, data):
        city_id = data.get('city')
        validated_data = super().to_internal_value(data)
        validated_data['city_id'] = city_id
        return validated_data

# USER REGISTERATION SERIALIZER--------------------------------->
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField( write_only = True, validators=[validate_password])
    password2 = serializers.CharField( write_only = True)
    
    class  Meta:
        model = User
        fields=['email', 'first_name', 'last_name', 'password','password2']
        
    def validate(self, attrs):
        password = attrs.get('password','')
        password2 = attrs.get('password2','')
        if password != password2:
            raise serializers.ValidationError('passwords do not match')
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            first_name = validated_data.get('first_name'),
            last_name = validated_data.get('last_name'),
            password = validated_data.get('password'),

        )
        return user
            
# LOGIN SERIALIZER--------------------------------->
class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length = 255, min_length=6)
    password = serializers.CharField(validators=[validate_password], write_only=True)
    full_name = serializers.CharField(max_length=255,read_only=True)
    access_token = serializers.CharField(max_length = 255, read_only = True)
    refresh_token = serializers.CharField(max_length = 255, read_only = True)
    
    class Meta:
        model = User
        fields=['email','password','full_name', 'refresh_token', 'access_token']
        
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        print(email)
        print(password)
        request=self.context.get('request')
        user = authenticate(request, email = email, password = password)
        if not user:
            raise AuthenticationFailed('invalid credintials try again')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        user_tokens = user.tokens()
        
        return{
            'email':user.email,
            'full_name':user.get_full_name,
            'access_token' : str(user_tokens.get('access')),
            'refresh_token':str(user_tokens.get('refresh'))
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'profile_image','last_login']

    profile_image = serializers.SerializerMethodField()

    def get_profile_image(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None
    
    
class UserPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone']

    def update(self, instance, validated_data):
        # Get the new phone number
        phone = validated_data.get('phone', None)
        
        if phone:
            # Update the phone field
            instance.phone = phone
            instance.save()
        
        return instance

# RESET PASSWORD SERIALIZER---------------------------------> 
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    
    class  Meta:
       fields=['email']
       
    def validate(self,attrs):
        email=attrs.get('email')
        if User.objects.filter(email = email):
            user = User.objects.get(email = email)
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request=self.context.get('request')
            site_domain=get_current_site(request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64':uidb64, 'token':token})
            abslink=f"http://{site_domain}{relative_link}"
            email_body=f"Hi use the link below to reset your password \n {abslink}"
            data={
                'email_body':email_body,
                'email_subject':'Reset Your Password',
                'to_email':user.email
            }
            send_normal_email(data)
            
        return super().validate(attrs)

# SET NEW PASSWORD SERIALIZER--------------------------------->
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6,write_only=True)
    confirm_password=serializers.CharField(max_length=100,min_length=6,write_only=True)
    uidb64=serializers.CharField(write_only=True)
    token=serializers.CharField(write_only=True)
    
    class Meta:
        fields=['password',
                'confirm_password',
                'uidb64',
                'token']
    def validate(self, attrs):
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            password = attrs.get('password')
            confirm_password=attrs.get('confirm_password')
            
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('reset link is invalid or has expired')
            if password != confirm_password:
                raise AuthenticationFailed("passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed('link is invalid or expired')

# USER PROFILE REGISTER SERIALIZER---------------------->

class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image']

    def update(self, instance, validated_data):
        # Get the new profile image
        profile_image = validated_data.get('profile_image', None)
        
        if profile_image:
            # If the instance already has a profile image, delete it
            if instance.profile_image:
                instance.profile_image.delete(save=False)
            
            # Update the profile image field
            instance.profile_image = profile_image
            instance.save()
        
        return instance
    
# USER ADDRESSES------------------------------------------>
class UserAddressSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = UserAddress
        fields = ['id', 'address']

    def validate(self, data):
        user = self.context['request'].user
        address_data = data.get('address')

        if address_data is None:
            raise serializers.ValidationError("Address data is required.")

        address_id = address_data.get('id')

        # Check if an address already exists for this user
        if address_id and UserAddress.objects.filter(user=user, address_id=address_id).exists():
            raise serializers.ValidationError("This address already exists for the user.")
        
        return data

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address, created = Address.objects.get_or_create(**address_data)
        user_address = UserAddress.objects.create(address=address, **validated_data)
        return user_address
    
# USER EMAIL UPDATE------------------------------------->

class UserEmailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUpdateCode
        fields = ['email']
    
    def create(self, validated_data):
        myuser = self.context['request'].user
        
        EmailUpdateCode.objects.filter(user=myuser).delete()
        # Send the OTP to the user's email
        Subject = "Ont Time passcode for Email verification"
        otpcode = generateOtp()
        email_body =f"HI {myuser.first_name} \n please verify your email with the \n one time passcode {otpcode}"
        from_email = settings.DEFAULT_FROM_EMAIL 

        d_email = EmailMessage(subject=Subject, body =email_body, from_email=from_email, to=(validated_data.get('email'),))
        d_email.send(fail_silently=True)

        emailUpdate = EmailUpdateCode.objects.create(
            user =  myuser,
            email = validated_data.get('email'),
            code = otpcode
        )
        return emailUpdate

class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        # Check if the old password is correct
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect"})

        # Ensure new password and confirm password match
        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "New password and confirm password do not match"})

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
# PROFESSIONAL SERIALIZERS-------------------------------->
class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ['id', 'license_number', 'insurance_number']
    
    def create(self, validated_data):
        # Get the current user from the request context
        user = self.context['request'].user
        
        # Check if a Professional with the same license_number already exists for this user
        if Professional.objects.filter(license_number=validated_data['license_number']).exists():
            raise serializers.ValidationError("A professional with this license number is already registered.")
        if Professional.objects.filter(insurance_number=validated_data['insurance_number']).exists():
            raise serializers.ValidationError("A professional with this license number is already registered.")
        if Professional.objects.filter(admin=user).exists():
            raise serializers.ValidationError("A professional with this license number is already registered.")
        # If no such Professional exists, create a new one
        validated_data['admin'] = user
        return Professional.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.license_number = validated_data.get('license_number', instance.license_number)
        instance.insurance_number = validated_data.get('insurance_number', instance.insurance_number)
        instance.save()
        return instance

# PROFESSIONAL SERVICES SERIALIZERS

class ProfessionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalService
        fields = ['id', 'serviceCatagory', 'serivce']

    def validate(self, data):
        # Get the current user as the professional
        professional = self.context['request'].user.professional

        # Check if the combination of professional and service already exists
        if ProfessionalService.objects.filter(
            professional=professional,
            service=data['serivce'],
            serviceCatagory=data['serviceCatagory']
        ).exists():
            raise serializers.ValidationError("This service is already registered for the professional.")

        return data

    def create(self, validated_data):
        # Set the professional field to the current user
        validated_data['professional'] = self.context['request'].user.professional
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Set the professional field to the current user
        validated_data['professional'] = self.context['request'].user.professional
        return super().update(instance, validated_data)
    

    # profile view


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code']

class ProvinceSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Province
        fields = ['id', 'name', 'code', 'country']

class CitySerializer(serializers.ModelSerializer):
    province = ProvinceSerializer(read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'province']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True, required=False)

    class Meta:
        model = UserAddress
>>>>>>> f4e4c0a3352cd10bb734dc50c164e5f0d5cfdc69
        fields = ['user', 'address']