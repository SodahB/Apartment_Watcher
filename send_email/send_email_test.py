import smtplib

HOST = "smtp.gmail.com"
PORT = 587

FROM_EMAIL = "SwedishSolidSnake@gmail.com"
TO_EMAIL = "jasmin.folkesson@stud.sti.se"
PASSWORD = "rfqi qrum sncd looo"

MESSAGE = """Subject: Mail sent using Python

Hello
I am sending this through python.


hehe

Thanks,
Apartment Watcher"""

try:
    smtp = smtplib.SMTP(HOST, PORT)

    status_code, response = smtp.ehlo()

    status_code, response = smtp.ehlo()
    print(f"[*] Echoing the server: {status_code} {response}")

    status_code, response = smtp.starttls()
    print(f"[*] Starting TLS connection {status_code} {response}")

    status_code, response = smtp.login(FROM_EMAIL, PASSWORD)
    print(f"[*] Logging in: {status_code} {response}")

    smtp.sendmail(FROM_EMAIL, TO_EMAIL, MESSAGE)
    print("[*] Email sent successfully!")

except smtplib.SMTPAuthenticationError as e:
    print(f"[!] Authentication failed: {e}")
except smtplib.SMTPException as e:
    print(f"[!] SMTP error: {e}")
except Exception as e:
    print(f"[!] An error occurred: {e}")
finally:
    smtp.quit()

