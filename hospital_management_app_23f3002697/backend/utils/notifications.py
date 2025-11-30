"""
Notification utilities for Email, Google Chat, and SMS
"""
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', SMTP_USERNAME)

# Google Chat webhook URL
GCHAT_WEBHOOK_URL = os.environ.get('GCHAT_WEBHOOK_URL', '')

# SMS configuration (using Twilio or similar)
SMS_PROVIDER = os.environ.get('SMS_PROVIDER', 'twilio')  # 'twilio' or 'custom'
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')

def send_email_notification(to_email, subject, message, html_message=None):
    """
    Send email notification
    """
    try:
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.warning("Email credentials not configured. Skipping email notification.")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        
        # Add plain text version
        text_part = MIMEText(message, 'plain')
        msg.attach(text_part)
        
        # Add HTML version if provided
        if html_message:
            html_part = MIMEText(html_message, 'html')
            msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_gchat_notification(message, webhook_url=None):
    """
    Send notification to Google Chat via webhook
    """
    try:
        webhook = webhook_url or GCHAT_WEBHOOK_URL
        
        if not webhook:
            logger.warning("Google Chat webhook URL not configured. Skipping GChat notification.")
            return False
        
        payload = {
            'text': message
        }
        
        response = requests.post(webhook, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info("Google Chat notification sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send Google Chat notification: {str(e)}")
        return False

def send_sms_notification(to_phone, message, provider=None):
    """
    Send SMS notification
    Supports Twilio and custom providers
    """
    try:
        provider = provider or SMS_PROVIDER
        
        if provider == 'twilio':
            return _send_twilio_sms(to_phone, message)
        else:
            logger.warning(f"SMS provider '{provider}' not implemented")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send SMS to {to_phone}: {str(e)}")
        return False

def _send_twilio_sms(to_phone, message):
    """
    Send SMS via Twilio
    """
    try:
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            logger.warning("Twilio credentials not configured. Skipping SMS notification.")
            return False
        
        from twilio.rest import Client
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        
        logger.info(f"SMS sent successfully to {to_phone} via Twilio")
        return True
        
    except ImportError:
        logger.warning("Twilio library not installed. Install with: pip install twilio")
        return False
    except Exception as e:
        logger.error(f"Failed to send SMS via Twilio: {str(e)}")
        return False

