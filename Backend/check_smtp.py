"""Check SMTP settings"""
from app.core.database import SessionLocal
from app.models import Company
from app.core.security import decrypt_password

db = SessionLocal()
try:
    company = db.query(Company).first()
    print(f'Company: {company.company_name}')
    print(f'SMTP Enabled: {company.smtp_enabled}')
    print(f'SMTP Host: {company.smtp_host}')
    print(f'SMTP Port: {company.smtp_port}')
    print(f'SMTP Username: {company.smtp_username}')
    print(f'Password configured: {bool(company.smtp_password)}')

    if company.smtp_password:
        try:
            decrypted = decrypt_password(company.smtp_password)
            print(f'Decrypted password length: {len(decrypted)} chars')
            print(f'Decrypted password (redacted): {"*" * len(decrypted)}')
        except Exception as e:
            print(f'Error decrypting: {e}')
finally:
    db.close()
