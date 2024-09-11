from django.core.mail import send_mail
from django.conf import settings
from app.models import User
import random


def send_otp_via_email(email):
    subject='your account verfication email'
    otp = random.randint(1000, 9999)
    message = f'Your OTP is {otp}'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])
    user = User.objects.get(email=email)
    user.otp = otp
    user.save()