def load_email_config():
    """Load email configuration from environment variables."""
    try:
        return {
            'from': os.environ['EMAIL_FROM'],
            'to': os.environ['EMAIL_TO'],
            'password': os.environ['EMAIL_PASSWORD'],
            'smtp_server': os.environ['SMTP_SERVER'],
            'smtp_port': int(os.environ['SMTP_PORT'])
        }
    except KeyError as e:
        logger.error(f"Missing required environment variable: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid SMTP port value: {e}")
        sys.exit(1)