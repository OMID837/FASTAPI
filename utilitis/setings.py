import os
import smtplib
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from email.mime.text import MIMEText

load_dotenv()  # <-- فایل شما env است

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY is not set in env file")

serializer = URLSafeTimedSerializer(SECRET_KEY)


def generate_activation_token(email: str):
    return serializer.dumps(email, salt="email-activate")


def verify_activation_token(token: str, max_age=3600):
    try:
        email = serializer.loads(token, salt="email-activate", max_age=max_age)
    except Exception:
        return None
    return email


# def send_email(subject, recipient, body):
#     msg = MIMEText(body, "plain")
#     msg["Subject"] = subject
#     msg["From"] = EMAIL_HOST_USER
#     msg["To"] = recipient
#
#     server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
#     if EMAIL_USE_TLS:
#         server.starttls()
#     server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
#     server.sendmail(EMAIL_HOST_USER, [recipient], msg.as_string())
#     server.quit()

executor = ThreadPoolExecutor(max_workers=5)


def send_email_thread(subject, recipient, body):
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = recipient

    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    if EMAIL_USE_TLS:
        server.starttls()
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    server.sendmail(EMAIL_HOST_USER, [recipient], msg.as_string())
    server.quit()
