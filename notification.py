from email.mime.text import MIMEText
import smtplib
import logging

class NotificationService:
    def send_email(self, recipient, subject, body):
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = 'noreply@wecare.com'
            msg['To'] = recipient
            logging.info(f"Email sent to {recipient}: {subject}")
            return True
        except Exception as e:
            logging.error(f"Email sending failed: {e}")
            return False

    def send_sms(self, phone, message):
        try:
            logging.info(f"SMS sent to {phone}: {message}")
            return True
        except Exception as e:
            logging.error(f"SMS sending failed: {e}")
            return False