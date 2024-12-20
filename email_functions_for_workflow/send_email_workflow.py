import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

def send_email(email, html_content):
    HOST = "smtp.gmail.com"
    PORT = 587

    FROM_EMAIL = "ApartmentWatcher@gmail.com"
    TO_EMAIL = email
    PASSWORD = os.getenv("APP_PASSWORD")

    # Check if the environment variable for PASSWORD is loaded
    if not PASSWORD:
        print("[!] No password found in environment variables.")
        return

    # creating an object of class MIMEMultipart
    MESSAGE = MIMEMultipart("alternative")

    # passing values to the message object as key-value pairs
    MESSAGE['Subject'] = 'Apartment Alerts'
    MESSAGE['From'] = FROM_EMAIL
    MESSAGE['To'] = TO_EMAIL

    # Check if the HTML content is provided and not empty
    if not html_content:
        print("[!] HTML content is empty, cannot send email.")
        return

    # converting plain-text to html-type
    html_part = MIMEText(html_content, 'html')

    # attach the html-content onto the message
    MESSAGE.attach(html_part)

    # sending the mail through SMTP
    try:
        smtp = smtplib.SMTP(HOST, PORT)

        # Greeting the server
        status_code, response = smtp.ehlo()
        print(f"[*] Echoing the server: {status_code} {response}")

        # Start TLS encryption
        status_code, response = smtp.starttls()
        print(f"[*] Starting TLS connection {status_code} {response}")

        # Logging in with the provided credentials
        status_code, response = smtp.login(FROM_EMAIL, PASSWORD)
        print(f"[*] Logging in: {status_code} {response}")

        # sending the email
        smtp.sendmail(FROM_EMAIL, TO_EMAIL, MESSAGE.as_string())
        print("[*] Email sent successfully!")

    except smtplib.SMTPAuthenticationError as e:
        print(f"[!] Authentication failed: {e}")
    except smtplib.SMTPException as e:
        print(f"[!] SMTP error: {e}")
    except Exception as e:
        print(f"[!] An error occurred: {e}")
    finally:
        smtp.quit()
