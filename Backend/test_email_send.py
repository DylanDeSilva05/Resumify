"""Test email sending directly"""
from app.core.database import SessionLocal
from app.models import Company
from app.core.security import decrypt_password
from app.services.email_service import EmailService

db = SessionLocal()
try:
    company = db.query(Company).first()
    print(f'Company: {company.company_name}')
    print(f'SMTP Enabled: {company.smtp_enabled}')
    print(f'SMTP Host: {company.smtp_host}')
    print(f'SMTP Port: {company.smtp_port}')
    print(f'SMTP Username: {company.smtp_username}')

    # Decrypt password
    smtp_password = decrypt_password(company.smtp_password)
    print(f'\nDecrypted password length: {len(smtp_password)} chars')

    # Create email service
    email_service = EmailService(
        smtp_host=company.smtp_host,
        smtp_port=company.smtp_port,
        smtp_user=company.smtp_username,
        smtp_password=smtp_password
    )

    print(f'\nEmail service enabled: {email_service.enabled}')

    # Try to send a test email
    print('\nAttempting to send test email...')
    result = email_service.send_email(
        to_email="dylandesilva05@gmail.com",  # Using the same email for testing
        subject="Test Email from Resumify - Direct Script Test",
        body="""Hello,

This is a test email sent directly from a Python script to verify your email configuration is working correctly.

Company: Demo Company
Test Type: Direct Script Test

If you received this email, your SMTP settings are configured correctly!

Best regards,
Resumify Team
""",
        from_name=company.smtp_from_name or company.company_name
    )

    print(f'\nEmail send result: {result}')
    if result:
        print('SUCCESS! Email was sent. Check your inbox!')
    else:
        print('FAILED! Email was not sent. Check the logs above for errors.')

finally:
    db.close()
