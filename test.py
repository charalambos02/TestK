def load_config():
    """Load and validate configuration from file with enhanced security."""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"Config file {CONFIG_FILE} not found")
        # Verify file permissions are secure (600 or less)
        if os.stat(CONFIG_FILE).st_mode & 0o777 > 0o600:
            raise PermissionError("Config file permissions are too permissive")
        config.read(CONFIG_FILE)
        # Validate required sections and values
        required = {
            'email': ['from', 'to', 'smtp_server', 'smtp_port'],
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
        except ValueError as e:
            raise ValueError(f"Invalid encryption key: {e}")
        return {
            'email': {
                'from': config.get('email', 'from'),
                'to': config.get('email', 'to'),
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
        logger.error(f"Configuration error: {e}")
        sys.exit(1)