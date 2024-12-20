import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

HOST = "smtp.gmail.com"
PORT = 587

FROM_EMAIL = "SwedishSolidSnake@gmail.com"
TO_EMAIL = "jasmin.folkesson@stud.sti.se"
PASSWORD = os.getenv("PASSWORD")

#creating a object of class MIMEMultipart
MESSAGE = MIMEMultipart("alternative")

#passing values to the message object as key-value pairs
MESSAGE['Subject'] = 'Testing html mail'
MESSAGE['From'] = FROM_EMAIL
MESSAGE['To'] = TO_EMAIL

#read the content from the html-file and save it as a html-variable
html = ""
with open("mail.html", "r") as file:
    html = file.read()

#converting plain-text to html-type
html_part = MIMEText(html, 'html')

#attach the html-content onto the message
MESSAGE.attach(html_part)

#sending the mail through SMTP
try:
    smtp = smtplib.SMTP(HOST, PORT)

    status_code, response = smtp.ehlo()

    status_code, response = smtp.ehlo()
    print(f"[*] Echoing the server: {status_code} {response}")

    status_code, response = smtp.starttls()
    print(f"[*] Starting TLS connection {status_code} {response}")

    status_code, response = smtp.login(FROM_EMAIL, PASSWORD)
    print(f"[*] Logging in: {status_code} {response}")
 
    #passing the message as a string
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
