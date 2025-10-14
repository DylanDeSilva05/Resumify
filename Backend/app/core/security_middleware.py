"""
Security middleware for OWASP compliance and enhanced security
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from app.services.security_service import SecurityService

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware implementing various security measures:
    - Security headers
    - Request size limits
    - Rate limiting (basic)
    - Input validation
    - SQL injection detection
    """

    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.security_service = SecurityService()
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add security measures"""
        start_time = time.time()

        # Check request size
        if hasattr(request, 'headers') and 'content-length' in request.headers:
            content_length = int(request.headers.get('content-length', 0))
            if content_length > self.max_request_size:
                logger.warning(f"Request size {content_length} exceeds limit {self.max_request_size}")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Request entity too large"
                )

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Basic rate limiting check (simplified)
        if not self.security_service.check_rate_limit(client_ip, max_requests=100, window_minutes=1):
            logger.warning(f"Rate limit exceeded for IP {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        # Check for suspicious query parameters
        if request.url.query:
            if self.security_service.check_sql_injection_patterns(request.url.query):
                self.security_service.log_security_event(
                    "SUSPICIOUS_QUERY",
                    None,
                    f"Suspicious query parameters: {request.url.query}",
                    client_ip
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request parameters"
                )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log security-related errors
            if isinstance(e, HTTPException) and e.status_code in [403, 401]:
                self.security_service.log_security_event(
                    "ACCESS_DENIED",
                    None,
                    f"Access denied: {str(e.detail)}",
                    client_ip
                )
            raise

        # Add security headers
        security_headers = self.security_service.get_security_headers()
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value

        # Add response time header for monitoring
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (load balancer/proxy)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()

        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip

        # Fallback to direct connection
        return request.client.host if request.client else "unknown"


class CORSSecurityMiddleware:
    """
    Secure CORS middleware with strict origin checking
    """

    def __init__(
        self,
        allowed_origins: list = None,
        allowed_methods: list = None,
        allowed_headers: list = None,
        allow_credentials: bool = True
    ):
        self.allowed_origins = allowed_origins or ["http://localhost:3000", "https://localhost:3000"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = allowed_headers or [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization"
        ]
        self.allow_credentials = allow_credentials

    def __call__(self, request: Request, call_next: Callable) -> StarletteResponse:
        """Process CORS with security checks"""
        origin = request.headers.get('origin')

        # Check if origin is allowed
        if origin and origin not in self.allowed_origins:
            logger.warning(f"CORS: Blocked request from unauthorized origin: {origin}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Origin not allowed"
            )

        return call_next(request)


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for input validation and sanitization
    """

    def __init__(self, app):
        super().__init__(app)
        self.security_service = SecurityService()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request inputs"""

        # Skip validation for certain paths
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)

        # Validate path parameters
        if len(request.url.path) > 2048:  # URL too long
            raise HTTPException(
                status_code=status.HTTP_414_REQUEST_URI_TOO_LONG,
                detail="Request URI too long"
            )

        # Check for path traversal attempts
        if "../" in request.url.path or "..\\" in request.url.path:
            self.security_service.log_security_event(
                "PATH_TRAVERSAL_ATTEMPT",
                None,
                f"Path traversal attempt: {request.url.path}",
                request.client.host if request.client else "unknown"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request path"
            )

        # Validate User-Agent header
        user_agent = request.headers.get('user-agent', '')
        if len(user_agent) > 512:  # Suspiciously long user agent
            logger.warning(f"Suspiciously long User-Agent: {user_agent[:100]}...")

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware specifically for adding security headers
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Comprehensive security headers
        security_headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",

            # Prevent page framing (clickjacking protection)
            "X-Frame-Options": "DENY",

            # XSS protection
            "X-XSS-Protection": "1; mode=block",

            # Force HTTPS (enable in production)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",

            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            ),

            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",

            # Feature policy
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "fullscreen=(self), "
                "payment=()"
            ),

            # Server identification
            "Server": "Resumify-Server",

            # Cache control for sensitive endpoints
            "Cache-Control": "no-store, no-cache, must-revalidate, private",
            "Pragma": "no-cache",
            "Expires": "0"
        }

        # Add all security headers
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value

        return response