# Add at the top of the file
from getpass import getpass
from typing import Dict, Any
import hashlib
import hmac
# Modify the load_config function
def load_config() -> Dict[str, Any]:
    """Load and validate configuration from file with enhanced security."""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"Config file {CONFIG_FILE} not found")
        # Verify file permissions
        if oct(os.stat(CONFIG_FILE).st_mode)[-3:] != '600':
            logger.warning("Insecure config file permissions detected")
        config.read(CONFIG_FILE)
        # Validate required sections exist
        for section in ['email', 'logging', 'encryption']:
            if section not in config:
                raise ValueError(f"Missing required section: {section}")
        # Environment variable alternative for sensitive data
        email_pass = os.getenv('EMAIL_PASSWORD') or config.get('email', 'password')
        return {
            'email': {
                'from': config.get('email', 'from'),
                'to': config.get('email', 'to'),
                'password': email_pass,
                'smtp_server': config.get('email', 'smtp_server'),
                'smtp_port': config.getint('email', 'smtp_port')
            },
            'logging': {
                'dir': config.get('logging', 'dir'),
                'file': config.get('logging', 'file')
            },
            'encryption': {
                'key': os.getenv('ENCRYPTION_KEY') or config.get('encryption', 'key')
            }
        }
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)