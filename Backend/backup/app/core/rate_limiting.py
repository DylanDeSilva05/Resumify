"""
Rate limiting middleware and utilities
"""
from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
import logging
from typing import Callable

from .config import settings

logger = logging.getLogger(__name__)

# Redis client for rate limiting
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_client_ip(request: Request) -> str:
    """
    Get client IP address for rate limiting

    Args:
        request: FastAPI request object

    Returns:
        str: Client IP address
    """
    # Check for forwarded IP first (behind proxy/load balancer)
    forwarded_ip = request.headers.get("X-Forwarded-For")
    if forwarded_ip:
        # Take the first IP in case of multiple
        return forwarded_ip.split(",")[0].strip()

    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to remote address
    return get_remote_address(request)


def get_user_or_ip(request: Request) -> str:
    """
    Get user ID if authenticated, otherwise IP address

    Args:
        request: FastAPI request object

    Returns:
        str: User identifier for rate limiting
    """
    # Try to get user from request state (if authenticated)
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"

    # Fall back to IP address
    return f"ip:{get_client_ip(request)}"


# Create limiter instance
limiter = Limiter(
    key_func=get_user_or_ip,
    storage_uri=settings.REDIS_URL,
    default_limits=["1000/hour", "100/minute"]
)


class RateLimitingMiddleware:
    """Custom rate limiting middleware for additional control"""

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_limit: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit

    async def __call__(self, request: Request, call_next: Callable):
        """
        Rate limiting middleware

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint

        Returns:
            Response or raises HTTPException if rate limited
        """
        client_id = get_user_or_ip(request)

        # Check if client is rate limited
        if await self._is_rate_limited(client_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        # Process request
        response = await call_next(request)

        # Record the request
        await self._record_request(client_id)

        return response

    async def _is_rate_limited(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limits

        Args:
            client_id: Client identifier

        Returns:
            bool: True if rate limited, False otherwise
        """
        try:
            # Check burst limit (sliding window)
            burst_key = f"burst:{client_id}"
            burst_count = redis_client.incr(burst_key)

            if burst_count == 1:
                redis_client.expire(burst_key, 10)  # 10 second window

            if burst_count > self.burst_limit:
                logger.warning(f"Burst rate limit exceeded for {client_id}")
                return True

            # Check per-minute limit
            minute_key = f"minute:{client_id}"
            minute_count = redis_client.incr(minute_key)

            if minute_count == 1:
                redis_client.expire(minute_key, 60)

            if minute_count > self.requests_per_minute:
                logger.warning(f"Per-minute rate limit exceeded for {client_id}")
                return True

            # Check per-hour limit
            hour_key = f"hour:{client_id}"
            hour_count = redis_client.incr(hour_key)

            if hour_count == 1:
                redis_client.expire(hour_key, 3600)

            if hour_count > self.requests_per_hour:
                logger.warning(f"Per-hour rate limit exceeded for {client_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Rate limiting check failed: {e}")
            # Allow request if Redis is down (fail open)
            return False

    async def _record_request(self, client_id: str) -> None:
        """
        Record request for analytics

        Args:
            client_id: Client identifier
        """
        try:
            # Could be used for analytics/monitoring
            analytics_key = f"analytics:{client_id}"
            redis_client.incr(analytics_key)
            redis_client.expire(analytics_key, 86400)  # 24 hours
        except Exception as e:
            logger.error(f"Failed to record request analytics: {e}")


def create_upload_rate_limiter(max_files_per_hour: int = 50) -> Callable:
    """
    Create rate limiter specifically for file uploads

    Args:
        max_files_per_hour: Maximum files per hour per user/IP

    Returns:
        Callable: Rate limiting function
    """
    async def upload_rate_limit(request: Request):
        client_id = get_user_or_ip(request)
        key = f"upload:{client_id}"

        try:
            count = redis_client.incr(key)
            if count == 1:
                redis_client.expire(key, 3600)  # 1 hour

            if count > max_files_per_hour:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Upload limit exceeded. Maximum {max_files_per_hour} files per hour."
                )

        except redis.RedisError as e:
            logger.error(f"Upload rate limiting failed: {e}")
            # Allow upload if Redis is down

    return upload_rate_limit


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded

    Args:
        request: FastAPI request
        exc: Rate limit exception

    Returns:
        JSON response with rate limit info
    """
    response = _rate_limit_exceeded_handler(request, exc)
    logger.warning(
        f"Rate limit exceeded for {get_client_ip(request)} on {request.url.path}"
    )
    return response