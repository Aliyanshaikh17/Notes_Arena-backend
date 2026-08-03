import random
from django.core.mail import send_mail
from django.conf import settings



def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
    subject = "Notes Arena - Password Reset OTP"

    message = f"""
Hello,

Your OTP is: {otp}

This OTP is valid for 5 minutes.

Thank You,
Notes Arena Team
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )




def verify_admin_credentials(username, password):
    return (
        username == settings.ADMIN_USERNAME
        and password == settings.ADMIN_PASSWORD
    )