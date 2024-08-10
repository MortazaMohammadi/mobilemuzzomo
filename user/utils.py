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

def send_code_to_user(email):
    Subject = "Ont Time passcode for Email verification"
    otp_code=generateOtp()
    print(otp_code)
    user = User.objects.get(email = email)
    current_site = 'Muzzomo.com'
    email_body =f"HI {user.first_name} thanks for your signing up on {current_site} please verify your email with the \n one time passcode {otp_code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    
    OneTimePassword.objects.create(user = user, code = otp_code)
    
    d_email = EmailMessage(subject=Subject, body =email_body, from_email=from_email, to=(email,))
    d_email.send(fail_silently=True)
    
def send_normal_email(data):
    email=EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()




def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if isinstance(exc, IntegrityError):
        response = {
            'detail': 'A unique constraint failed. Please ensure that the address is not already associated with the user.'
        }
        return response

    return response