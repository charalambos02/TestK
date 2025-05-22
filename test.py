def load_config() -> dict:
    """Load and validate application configuration.
    Returns:
        dict: Nested dictionary containing validated configuration sections
    Raises:
        FileNotFoundError: If config file is missing
        ValueError: For invalid configuration values
        PermissionError: For insecure file permissions
    """
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file {CONFIG_FILE} not found")
    # Verify secure file permissions (readable only by owner)
    if (os.stat(CONFIG_FILE).st_mode & 0o777) > 0o600:
        raise PermissionError("Insecure config file permissions")
    try:
        config.read(CONFIG_FILE)
        return validate_config(config)
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise