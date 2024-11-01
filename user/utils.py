import random
from django.core.mail import EmailMessage
from MuzzomoBackend import settings
from django.db import IntegrityError
from rest_framework.views import exception_handler
from user.models import OneTimePassword, User 

def generateOtp():
    otp=""
    for i in range(6):
        otp +=str(random.randint(1,9))
    return otp

# def send_code_to_user(email):
#     Subject = "Ont Time passcode for Email verification"
#     otp_code=generateOtp()
#     print(otp_code)
#     user = User.objects.get(email = email)
#     current_site = 'Muzzomo.com'
#     email_body =f"HI {user.first_name} thanks for your signing up on {current_site} please verify your email with the \n one time passcode {otp_code}"
#     from_email = settings.DEFAULT_FROM_EMAIL
    
#     OneTimePassword.objects.create(user = user, code = otp_code)
    
#     d_email = EmailMessage(subject=Subject, body =email_body, from_email=from_email, to=(email,))
#     d_email.send(fail_silently=True)
    
# def send_normal_email(data):
#     email=EmailMessage(
#         subject=data['email_subject'],
#         body=data['email_body'],
#         from_email=settings.EMAIL_HOST_USER,
#         to=[data['to_email']]
#     )
#     email.send()
def send_code_to_user(email):
    subject = "One-Time Passcode for Email Verification"
    otp_code = generateOtp()
    print(f"Generated OTP: {otp_code}")  # For debugging purposes

    try:
        user = User.objects.get(email=email)
        current_site = 'Muzzomo.com'
        email_body = (
            f"Hi {user.first_name},\n\n"
            f"Thanks for signing up on {current_site}. "
            f"Please verify your email with the following OTP code: {otp_code}"
        )

        # Save OTP to database
        OneTimePassword.objects.create(user=user, code=otp_code)

        # Create and send the email
        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email.send(fail_silently=False)  # Set to False to catch errors

    except User.DoesNotExist:
        print(f"No user found with email: {email}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
        
def send_normal_email(data):
    try:
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            from_email=settings.EMAIL_HOST_USER,
            to=[data['to_email']],
        )
        email.send(fail_silently=False)  # Catch exceptions for debugging

    except Exception as e:
        print(f"Failed to send email: {str(e)}")




def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if isinstance(exc, IntegrityError):
        response = {
            'detail': 'A unique constraint failed. Please ensure that the address is not already associated with the user.'
        }
        return response

    return response
