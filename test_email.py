
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def test_email():
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAILS", "").split(",")[0] # Use first one

    if not sender_email or not sender_password:
        print("Error: EMAIL_USER or EMAIL_PASSWORD not set in .env")
        return

    print(f"Testing email...")
    print(f"From: {sender_email}")
    print(f"To: {recipient_email}")
    
    msg = MIMEMultipart()
    msg["Subject"] = "NaviCard AI - Test Email"
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg.attach(MIMEText("If you see this, email sending works!", "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            print("Logging in...")
            server.login(sender_email, sender_password)
            print("Sending...")
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Success! Email sent.")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_email()
