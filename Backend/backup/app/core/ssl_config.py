"""
SSL/TLS Configuration for HTTPS support
"""
import os
import ssl
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class SSLConfig:
    """SSL/TLS configuration management"""

    def __init__(self):
        self.cert_dir = Path("ssl_certificates")
        self.cert_dir.mkdir(exist_ok=True)

    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for HTTPS

        Returns:
            Optional[ssl.SSLContext]: SSL context if certificates are available
        """
        cert_file = self.cert_dir / "server.crt"
        key_file = self.cert_dir / "server.key"

        if not cert_file.exists() or not key_file.exists():
            logger.warning("SSL certificates not found. Generating self-signed certificates...")
            self.generate_self_signed_cert()

        if cert_file.exists() and key_file.exists():
            try:
                # Create SSL context
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(str(cert_file), str(key_file))

                # Security settings
                context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
                context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
                context.set_default_verify_paths()

                logger.info("SSL context created successfully")
                return context

            except Exception as e:
                logger.error(f"Failed to create SSL context: {e}")
                return None

        return None

    def generate_self_signed_cert(self) -> bool:
        """
        Generate self-signed SSL certificate for development

        Returns:
            bool: True if certificate was generated successfully
        """
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import datetime

            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )

            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Development"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Resumify HR System"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])

            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())

            # Write certificate to file
            cert_file = self.cert_dir / "server.crt"
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))

            # Write private key to file
            key_file = self.cert_dir / "server.key"
            with open(key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            # Set appropriate permissions
            os.chmod(key_file, 0o600)  # Private key should be read-only by owner
            os.chmod(cert_file, 0o644)  # Certificate can be world-readable

            logger.info("Self-signed SSL certificate generated successfully")
            logger.warning("Using self-signed certificate - not suitable for production!")
            return True

        except ImportError:
            logger.error("cryptography package required for SSL certificate generation")
            logger.info("Install with: pip install cryptography")
            return False
        except Exception as e:
            logger.error(f"Failed to generate SSL certificate: {e}")
            return False

    def get_ssl_files(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get paths to SSL certificate files

        Returns:
            Tuple[Optional[str], Optional[str]]: (cert_file, key_file) paths
        """
        cert_file = self.cert_dir / "server.crt"
        key_file = self.cert_dir / "server.key"

        if cert_file.exists() and key_file.exists():
            return str(cert_file), str(key_file)

        return None, None

    def verify_ssl_setup(self) -> bool:
        """
        Verify SSL setup is working

        Returns:
            bool: True if SSL is properly configured
        """
        context = self.get_ssl_context()
        return context is not None

    @staticmethod
    def get_production_ssl_config() -> dict:
        """
        Get production SSL configuration recommendations

        Returns:
            dict: Production SSL configuration
        """
        return {
            "description": "Production SSL Configuration",
            "recommendations": [
                "Use certificates from a trusted CA (Let's Encrypt, DigiCert, etc.)",
                "Enable HTTP Strict Transport Security (HSTS)",
                "Use strong cipher suites",
                "Disable weak protocols (SSLv2, SSLv3, TLSv1.0, TLSv1.1)",
                "Implement proper certificate validation",
                "Set up automatic certificate renewal",
                "Use Certificate Transparency monitoring"
            ],
            "nginx_config_example": {
                "ssl_certificate": "/path/to/certificate.crt",
                "ssl_certificate_key": "/path/to/private.key",
                "ssl_protocols": "TLSv1.2 TLSv1.3",
                "ssl_ciphers": "ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512",
                "ssl_prefer_server_ciphers": "off",
                "ssl_session_cache": "shared:SSL:10m",
                "ssl_session_timeout": "10m",
                "add_header": "Strict-Transport-Security 'max-age=31536000' always"
            },
            "uvicorn_production_command": [
                "uvicorn app.main:app",
                "--host 0.0.0.0",
                "--port 443",
                "--ssl-keyfile=/path/to/private.key",
                "--ssl-certfile=/path/to/certificate.crt",
                "--ssl-version=3",  # TLS only
                "--ssl-cert-reqs=0",  # No client cert required
                "--ssl-ca-certs=/path/to/ca-bundle.crt"
            ]
        }


def setup_ssl_for_development() -> Optional[ssl.SSLContext]:
    """
    Quick setup function for development SSL

    Returns:
        Optional[ssl.SSLContext]: SSL context for development
    """
    ssl_config = SSLConfig()
    return ssl_config.get_ssl_context()


def print_ssl_setup_instructions():
    """Print instructions for SSL setup"""
    instructions = """
    SSL/TLS Setup Instructions:

    DEVELOPMENT:
    1. Run the application - self-signed certificates will be generated automatically
    2. Access https://localhost:8000 (browser will show security warning)
    3. Accept the self-signed certificate for testing

    PRODUCTION:
    1. Obtain SSL certificates from a trusted Certificate Authority
    2. Place certificate files in ssl_certificates/ directory:
       - server.crt (certificate file)
       - server.key (private key file)
    3. Or configure reverse proxy (nginx/apache) for SSL termination
    4. Update firewall rules to allow HTTPS traffic (port 443)

    Let's Encrypt (Free SSL):
    1. Install certbot: sudo apt-get install certbot
    2. Get certificate: sudo certbot certonly --standalone -d yourdomain.com
    3. Copy certificates to ssl_certificates/ directory
    4. Set up auto-renewal: sudo crontab -e
       Add: 0 12 * * * /usr/bin/certbot renew --quiet

    Security Best Practices:
    - Never commit private keys to version control
    - Use strong cipher suites
    - Enable HSTS headers
    - Monitor certificate expiration
    - Implement proper certificate validation
    """
    print(instructions)