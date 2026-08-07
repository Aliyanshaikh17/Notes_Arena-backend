import random
import resend
from django.conf import settings

# Configure Resend API Key
resend.api_key = settings.RESEND_API_KEY


def generate_otp():
    return str(random.randint(100000, 999999))


# Forgot Password OTP
def send_otp_email(email, otp):

    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": "Notes Arena - Password Reset OTP",
            "html": f"""
                <h2>Notes Arena</h2>

                <p>Hello,</p>

                <p>Your OTP for password reset is:</p>

                <h1>{otp}</h1>

                <p>This OTP is valid for <b>5 minutes</b>.</p>

                <p>Please do not share this OTP with anyone.</p>

                <br>

                <p>Regards,<br>Notes Arena Team</p>
            """
        })

    except Exception as e:
        print(f"Failed to send Password Reset OTP: {e}")


# Registration OTP
def send_registration_otp_email(email, full_name, otp):

    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": "Notes Arena - Registration OTP",
            "html": f"""
                <h2>Welcome to Notes Arena</h2>

                <p>Hello <b>{full_name}</b>,</p>

                <p>Thank you for registering with Notes Arena.</p>

                <p>Your Registration OTP is:</p>

                <h1>{otp}</h1>

                <p>This OTP is valid for <b>5 minutes</b>.</p>

                <p>Please do not share this OTP with anyone.</p>

                <br>

                <p>Regards,<br>Notes Arena Team</p>
            """
        })

    except Exception as e:
        print(f"Failed to send Registration OTP: {e}")


def verify_admin_credentials(username, password):
    return (
        username == settings.ADMIN_USERNAME
        and password == settings.ADMIN_PASSWORD
    )