#!/usr/bin/env python3
"""
Security setup script for Resumify HR System
Installs and configures all security features from the proposal
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.core.ssl_config import SSLConfig, print_ssl_setup_instructions
from app.core.database import init_db
from app.models.user import UserType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecuritySetup:
    """Security setup and configuration manager"""

    def __init__(self):
        self.ssl_config = SSLConfig()

    def install_dependencies(self):
        """Install security-related dependencies"""
        logger.info("Installing security dependencies...")

        dependencies = [
            "pyotp==2.9.0",
            "qrcode[pil]==7.4.2",
            "cryptography==41.0.7"
        ]

        for dep in dependencies:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                logger.info(f"✓ Installed {dep}")
            except subprocess.CalledProcessError as e:
                logger.error(f"✗ Failed to install {dep}: {e}")

    def setup_ssl_certificates(self):
        """Setup SSL certificates for HTTPS"""
        logger.info("Setting up SSL certificates...")

        if self.ssl_config.verify_ssl_setup():
            logger.info("✓ SSL certificates already configured")
            return True

        if self.ssl_config.generate_self_signed_cert():
            logger.info("✓ Self-signed SSL certificates generated")
            logger.warning("⚠ Self-signed certificates are for development only!")
            return True
        else:
            logger.error("✗ Failed to generate SSL certificates")
            return False

    def setup_database(self):
        """Initialize database with security enhancements"""
        logger.info("Setting up database with security features...")

        try:
            # Initialize database tables
            init_db()
            logger.info("✓ Database tables created")

            # Create default admin user if not exists
            self.create_default_admin()

            return True
        except Exception as e:
            logger.error(f"✗ Database setup failed: {e}")
            return False

    def create_default_admin(self):
        """Create default admin user with 2FA ready"""
        from sqlalchemy.orm import sessionmaker
        from app.core.database import engine
        from app.models.user import User
        from app.core.security import get_password_hash

        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()

        try:
            # Check if admin user exists
            admin = db.query(User).filter(User.username == "admin").first()

            if not admin:
                # Create admin user
                admin_user = User(
                    username="admin",
                    email="admin@resumify.local",
                    full_name="System Administrator",
                    hashed_password=get_password_hash("Admin123!"),  # Change this!
                    user_type=UserType.ADMIN_HR,
                    is_active=True
                )
                db.add(admin_user)
                db.commit()

                logger.info("✓ Default admin user created")
                logger.warning("⚠ Default admin password is 'Admin123!' - CHANGE IT IMMEDIATELY!")
                logger.info(f"✓ Admin user: {admin_user.username} ({admin_user.email})")
            else:
                logger.info("✓ Admin user already exists")

        except Exception as e:
            logger.error(f"✗ Failed to create admin user: {e}")
            db.rollback()
        finally:
            db.close()

    def setup_security_middleware(self):
        """Setup security middleware configuration"""
        logger.info("Configuring security middleware...")

        middleware_config = """
# Add these middleware to your FastAPI app in main.py:

from app.core.security_middleware import (
    SecurityMiddleware,
    SecurityHeadersMiddleware,
    InputValidationMiddleware
)

# Add to FastAPI app
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputValidationMiddleware)
app.add_middleware(SecurityMiddleware, max_request_size=10*1024*1024)  # 10MB limit

# CORS configuration (update allowed origins for production)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],  # Update for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
"""

        with open("middleware_setup.txt", "w") as f:
            f.write(middleware_config)

        logger.info("✓ Security middleware configuration saved to middleware_setup.txt")

    def setup_environment_variables(self):
        """Setup required environment variables"""
        logger.info("Setting up environment variables...")

        env_template = """
# Security Environment Variables for Resumify HR System

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/resumify_db

# JWT Security
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload Security
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=pdf,doc,docx
MAX_FILE_SIZE=10485760  # 10MB

# SSL Configuration
SSL_ENABLED=true
SSL_CERT_FILE=ssl_certificates/server.crt
SSL_KEY_FILE=ssl_certificates/server.key

# Security Settings
RATE_LIMIT_ENABLED=true
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=15

# 2FA Settings
TWO_FA_ISSUER="Resumify HR System"

# Development/Production Mode
DEBUG=false
ENVIRONMENT=production

# CORS Settings (Update for production)
ALLOWED_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""

        with open(".env.example", "w") as f:
            f.write(env_template)

        logger.info("✓ Environment template saved to .env.example")
        logger.warning("⚠ Copy .env.example to .env and update values for your environment")

    def generate_security_documentation(self):
        """Generate security documentation"""
        logger.info("Generating security documentation...")

        security_doc = """
# Resumify HR System - Security Implementation

## 🔒 Security Features Implemented

### 1. Two-Factor Authentication (2FA)
- ✅ TOTP support (Google Authenticator, Authy)
- ✅ QR code generation for easy setup
- ✅ Backup codes for account recovery
- ✅ 2FA management endpoints

**Setup 2FA:**
1. POST /api/v1/2fa/setup - Initialize 2FA
2. GET /api/v1/2fa/qr-code - Get QR code image
3. POST /api/v1/2fa/verify - Verify and enable 2FA

### 2. Role-Based Access Control (RBAC)
- ✅ 3-tier role system as per proposal:
  - **ADMIN_HR**: Full system access, user management
  - **STANDARD_HR**: Standard HR operations, CV analysis
  - **RECRUITER_HR**: CV screening, interview scheduling
- ✅ Granular permissions system
- ✅ Role hierarchy enforcement

**Role Permissions:**
- Use `@Depends(require_permission(Permission.CREATE_USER))` for endpoint protection
- Use `@Depends(get_admin_hr_user)` for role-based access

### 3. Enhanced Input Validation & OWASP Compliance
- ✅ Request size limits
- ✅ SQL injection detection
- ✅ Path traversal protection
- ✅ Rate limiting (basic implementation)
- ✅ Comprehensive security headers
- ✅ Input sanitization

### 4. HTTPS/TLS Configuration
- ✅ SSL certificate generation (self-signed for dev)
- ✅ TLS 1.2+ enforcement
- ✅ Strong cipher suites
- ✅ HSTS headers

### 5. Account Security
- ✅ Account lockout after failed attempts
- ✅ Password strength validation
- ✅ Session management
- ✅ Security event logging

## 🚀 Production Deployment Security Checklist

### SSL/TLS Setup
- [ ] Obtain production SSL certificates from trusted CA
- [ ] Configure strong cipher suites
- [ ] Enable HSTS headers
- [ ] Set up certificate auto-renewal

### Environment Security
- [ ] Change default admin password
- [ ] Generate secure JWT secret key
- [ ] Configure production database with SSL
- [ ] Set up proper CORS origins
- [ ] Enable rate limiting with Redis
- [ ] Configure log rotation

### Infrastructure Security
- [ ] Configure firewall rules
- [ ] Enable database encryption at rest
- [ ] Set up monitoring and alerting
- [ ] Implement backup encryption
- [ ] Configure reverse proxy (nginx/apache)

### Application Security
- [ ] Enable 2FA for all admin accounts
- [ ] Review and test all endpoints
- [ ] Set up security scanning (SAST/DAST)
- [ ] Configure content security policy
- [ ] Enable audit logging

## 📝 Usage Examples

### Protect Endpoint with Permission
```python
@router.post("/admin-only")
async def admin_endpoint(
    current_user: User = Depends(require_permission(Permission.MANAGE_SYSTEM_SETTINGS))
):
    return {"message": "Admin access granted"}
```

### Role-Based Endpoint Protection
```python
@router.get("/hr-dashboard")
async def hr_dashboard(
    current_user: User = Depends(get_standard_hr_user)
):
    return {"dashboard": "Standard HR or higher"}
```

### 2FA Verification in Login
```python
@router.post("/login")
async def login(request: LoginRequest):
    # Authenticate user
    user = authenticate_user(request.username, request.password)

    # Check if 2FA required
    if user.two_fa_enabled:
        if not request.totp_code:
            return {"two_fa_required": True}

        # Verify 2FA code
        if not verify_totp_code(user.two_fa_secret, request.totp_code):
            raise HTTPException(401, "Invalid 2FA code")

    # Generate access token
    token = create_access_token(user.id)
    return {"access_token": token}
```

## 🔧 Configuration Files

### Environment Variables (.env)
See .env.example for complete configuration template

### SSL Configuration
Self-signed certificates are generated automatically for development.
For production, place certificates in ssl_certificates/ directory.

### Database Migrations
Run database migrations to add security fields:
```bash
alembic revision --autogenerate -m "Add security features"
alembic upgrade head
```

## 🛡️ Security Monitoring

### Log Events to Monitor
- Failed login attempts
- 2FA setup/disable events
- Permission denied events
- Suspicious request patterns
- SSL certificate expiration

### Metrics to Track
- Authentication success/failure rates
- 2FA adoption rate
- API response times
- Rate limit violations
- Security header compliance

## 📞 Support

For security issues or questions:
1. Check logs in logs/app.log
2. Review security event logs
3. Verify SSL certificate status
4. Test 2FA functionality
5. Validate role permissions

Remember: Security is an ongoing process. Regularly update dependencies,
monitor for vulnerabilities, and review access patterns.
"""

        with open("SECURITY.md", "w") as f:
            f.write(security_doc)

        logger.info("✓ Security documentation saved to SECURITY.md")

    def run_setup(self):
        """Run complete security setup"""
        logger.info("🔒 Starting Resumify HR System Security Setup...")

        # Setup steps
        steps = [
            ("Installing Dependencies", self.install_dependencies),
            ("Setting up SSL Certificates", self.setup_ssl_certificates),
            ("Configuring Database", self.setup_database),
            ("Setting up Middleware", self.setup_security_middleware),
            ("Creating Environment Template", self.setup_environment_variables),
            ("Generating Documentation", self.generate_security_documentation)
        ]

        success_count = 0
        for step_name, step_func in steps:
            logger.info(f"\n📋 {step_name}...")
            try:
                if step_func():
                    success_count += 1
                    logger.info(f"✅ {step_name} completed")
                else:
                    logger.warning(f"⚠️ {step_name} completed with warnings")
            except Exception as e:
                logger.error(f"❌ {step_name} failed: {e}")

        # Summary
        logger.info(f"\n🎉 Security setup completed: {success_count}/{len(steps)} steps successful")

        if success_count == len(steps):
            logger.info("✅ All security features have been implemented successfully!")
            logger.info("\n📚 Next steps:")
            logger.info("1. Review and update .env file with your configuration")
            logger.info("2. Change the default admin password")
            logger.info("3. Configure production SSL certificates")
            logger.info("4. Test 2FA setup with your authenticator app")
            logger.info("5. Review SECURITY.md for deployment guidelines")
        else:
            logger.warning("⚠️ Some setup steps failed. Check logs above for details.")

        print_ssl_setup_instructions()


if __name__ == "__main__":
    setup = SecuritySetup()
    setup.run_setup()