def send_email(config, subject, body, max_retries=3):
    """Send email with enhanced error handling and security."""
    try:
        if not all(k in config['email'] for k in ['from', 'to', 'password', 'smtp_server', 'smtp_port']):
            raise ValueError("Missing required email configuration parameters")
        msg = f"From: {config['email']['from']}\nTo: {config['email']['to']}\nSubject: {subject}\n\n{body}"
        for attempt in range(max_retries):
            try:
                with smtplib.SMTP_SSL(
                    host=config['email']['smtp_server'],
                    port=config['email']['smtp_port'],
                    timeout=10
                ) as server:
                    server.login(
                        user=config['email']['from'],
                        password=config['email']['password']
                    )
                    server.sendmail(
                        config['email']['from'],
                        config['email']['to'],
                        msg
                    )
                    logger.info("Email notification sent successfully")
                    return True
            except (smtplib.SMTPException, TimeoutError) as e:
                logger.warning(f"Email attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))  # Exponential backoff
                else:
                    raise
    except Exception as e:
        logger.error(f"Failed to send email after {max_retries} attempts: {e}")
        return False