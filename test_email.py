import os
import smtplib
from email.message import EmailMessage


GMAIL_USERNAME = os.environ["GMAIL_USERNAME"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

recipient = GMAIL_USERNAME

message = EmailMessage()
message["Subject"] = "BYU-Idaho Faculty Job Alert - TEST"
message["From"] = GMAIL_USERNAME
message["To"] = recipient

message.set_content(
    """This is a test email from your BYU-Idaho Faculty Job Alert.

If you received this message, Gmail is configured correctly.

The next step will be connecting this to the Workday job scraper.
"""
)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
    smtp.send_message(message)

print("Test email sent successfully!")
