def send_email(config, subject, body, max_retries=3):
    """Send email with proper error handling and retry logic."""
    email_cfg = config['email']
    message = f"Subject: {subject}\n\n{body}"
    for attempt in range(max_retries):
        try:
            with smtplib.SMTP(
                host=email_cfg['smtp_server'],
                port=email_cfg['smtp_port']
            ) as server:
                server.starttls()
                server.login(
                    email_cfg['from'],
                    email_cfg['password']
                )
                server.sendmail(
                    email_cfg['from'],
                    email_cfg['to'],
                    message
                )
                logger.info("Email sent successfully")
                return True
        except Exception as e:
            logger.warning(
                f"Email send attempt {attempt + 1} failed: {str(e)}"
            )
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    logger.error("All email send attempts failed")
    return False