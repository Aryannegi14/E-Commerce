# store/utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, otp):
    subject = "Your OTP Code"
    message = f"Your OTP code is: {otp}"
    from_email = settings.DEFAULT_FROM_EMAIL  # Or you can specify your email here
    recipient_list = [email]
    
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        raise e  # Optionally raise the exception if you want to handle it further
