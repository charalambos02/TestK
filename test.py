def send_email(config, subject, body, max_retries=3):
    """Send email with retry logic and proper error handling."""
    email_cfg = config['email']
    message = f"Subject: {subject}\n\n{body}"
    for attempt in range(max_retries):
        try:
            with smtplib.SMTP(
                host=email_cfg['smtp_server'],
                port=email_cfg['smtp_port'],
                timeout=30
            ) as server:
                server.starttls()
                server.login(email_cfg['from'], email_cfg['password'])
                server.sendmail(
                    email_cfg['from'],
                    email_cfg['to'],
                    message
                )
                logger.info("Email sent successfully")
                return True
        except smtplib.SMTPException as e:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(
                f"Email send attempt {attempt + 1} failed: {e}. "
                f"Retrying in {wait_time} seconds..."
            )
            time.sleep(wait_time)
    logger.error(f"Failed to send email after {max_retries} attempts")
    return False