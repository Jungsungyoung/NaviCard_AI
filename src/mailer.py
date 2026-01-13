
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

def send_email(subject, html_content, recipient_list=None):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    if recipient_list is None:
        recipient_list = os.getenv("RECIPIENT_EMAILS", "").split(",")
    
    if not sender_email or not sender_password or not recipient_list:
        print("[Mailer] Error: Missing email configuration (EMAIL_USER, EMAIL_PASSWORD, or RECIPIENT_EMAILS).")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipient_list)

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        print(f"[*] Sending email to {len(recipient_list)} recipients...")
        # Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_list, msg.as_string())
        print("[*] Email sent successfully.")
        return True
    except Exception as e:
        print(f"[Mailer] Failed to send email: {e}")
        return False
