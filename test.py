def load_config():
    """Load and validate configuration from file with enhanced security checks."""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"Config file {CONFIG_FILE} not found")
        # Verify config file permissions (should be 600)
        if os.stat(CONFIG_FILE).st_mode & 0o777 != 0o600:
            logger.warning(f"Insecure permissions on {CONFIG_FILE}. Recommended: 600")
        config.read(CONFIG_FILE)
        # Validate required sections and values
        required = {
            'email': ['from', 'to', 'password', 'smtp_server', 'smtp_port'],
            'logging': ['dir', 'file'],
            'encryption': ['key']
        }
        for section, keys in required.items():
            if section not in config:
                raise ValueError(f"Missing required section: {section}")
            for key in keys:
                if not config.get(section, key, fallback=None):
                    raise ValueError(f"Missing required key: {section}.{key}")
        # Validate encryption key format
        try:
            Fernet(config.get('encryption', 'key'))
        except:
            raise ValueError("Invalid Fernet key format")
        return {
            'email': {
                'from': config.get('email', 'from'),
                'to': config.get('email', 'to'),
                'password': os.getenv('EMAIL_PASSWORD') or config.get('email', 'password'),
                'smtp_server': config.get('email', 'smtp_server'),
                'smtp_port': config.getint('email', 'smtp_port')
            },
            # ... rest of config
        }
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)