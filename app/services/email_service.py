"""
Email service using Gmail SMTP via fastapi-mail.
Sends: welcome emails, order confirmations.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def _send_email(to_email: str, subject: str, html_body: str):
    """Internal helper to send an email via SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.MAIL_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.starttls()
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.sendmail(settings.MAIL_FROM, to_email, msg.as_string())

def send_welcome_email(email: str, full_name: str):
    """Send a welcome email after registration."""
    subject = "Welcome to Our Store! 🎉"
    html = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <h2 style="color: #4F46E5;">Welcome, {full_name}!</h2>
        <p>Thank you for registering. Your account is ready.</p>
        <p>Start shopping now and enjoy the best deals!</p>
        <a href="{settings.FRONTEND_URL}" 
           style="background:#4F46E5;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;">
           Shop Now
        </a>
        <p style="color:#888;margin-top:20px;">— The E-Commerce Team</p>
    </body></html>
    """
    _send_email(email, subject, html)

def send_order_confirmation_email(email: str, full_name: str, order_id: int, total: float):
    """Send order confirmation after placing an order."""
    subject = f"Order #{order_id} Confirmed ✅"
    html = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <h2 style="color: #10B981;">Order Confirmed!</h2>
        <p>Hi {full_name}, your order has been placed successfully.</p>
        <div style="background:#F3F4F6;padding:16px;border-radius:8px;">
            <p><strong>Order ID:</strong> #{order_id}</p>
            <p><strong>Total Amount:</strong> ₹{total:.2f}</p>
        </div>
        <p>We'll notify you when your order ships.</p>
        <a href="{settings.FRONTEND_URL}/orders/{order_id}"
           style="background:#10B981;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;">
           Track Order
        </a>
        <p style="color:#888;margin-top:20px;">— The E-Commerce Team</p>
    </body></html>
    """
    _send_email(email, subject, html)
