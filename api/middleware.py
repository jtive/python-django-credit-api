from datetime import datetime, timedelta
from typing import Optional, cast
from django.http import JsonResponse, HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware for write operations."""

    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        # Only apply rate limiting to write operations
        if not self._is_write_operation(request.method or ""):
            return None

        client_id = self._get_client_id(request)
        max_requests = getattr(settings, "RATE_LIMIT_MAX_REQUESTS", 1000)
        window_hours = getattr(settings, "RATE_LIMIT_WINDOW_HOURS", 24)

        if not self._is_allowed(client_id, max_requests, window_hours):
            remaining = self._get_remaining_requests(
                client_id, max_requests, window_hours
            )

            logger.warning(
                f"Rate limit exceeded for client {client_id}. "
                f"Remaining requests: {remaining}"
            )

            response_data = {
                "error": "Rate limit exceeded",
                "message": (
                    f"You have exceeded the maximum number"
                    f" of write operations "
                    f"({max_requests} per day). Please try again tomorrow."
                ),
                "remainingRequests": remaining,
                "resetTime": (datetime.utcnow() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
            }

            return JsonResponse(response_data, status=429)

        return None

    def _is_write_operation(self, method: str) -> bool:
        """Check if the HTTP method is a write operation."""
        return method.upper() in ["POST", "PUT", "PATCH", "DELETE"]

    def _get_client_id(self, request: HttpRequest) -> str:
        """Get client identifier from request."""
        # Try to get client IP address
        client_ip = self._get_client_ip(request)
        return client_ip or "unknown"

    def _get_client_ip(self, request: HttpRequest) -> Optional[str]:
        """Extract client IP address from request."""
        # Check for forwarded IP headers
        x_forwarded_for = cast(
            Optional[str], request.META.get("HTTP_X_FORWARDED_FOR")
        )
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        x_real_ip = cast(Optional[str], request.META.get("HTTP_X_REAL_IP"))
        if x_real_ip:
            return x_real_ip

        # Fall back to remote address
        return cast(Optional[str], request.META.get("REMOTE_ADDR"))

    def _is_allowed(
        self, client_id: str, max_requests: int, window_hours: int
    ) -> bool:
        """Check if client is allowed to make a request."""
        cache_key = f"rate_limit:{client_id}"
        now = datetime.utcnow()
        window_start = now - timedelta(hours=window_hours)

        # Get existing requests
        requests = cache.get(cache_key, [])

        # Filter requests within the time window
        recent_requests = [
            req_time for req_time in requests if req_time > window_start
        ]

        # Check if under limit
        if len(recent_requests) >= max_requests:
            return False

        # Add current request
        recent_requests.append(now)
        cache.set(cache_key, recent_requests, timeout=window_hours * 3600)

        return True

    def _get_remaining_requests(
        self, client_id: str, max_requests: int, window_hours: int
    ) -> int:
        """Get remaining requests for client."""
        cache_key = f"rate_limit:{client_id}"
        now = datetime.utcnow()
        window_start = now - timedelta(hours=window_hours)

        # Get existing requests
        requests = cache.get(cache_key, [])

        # Filter requests within the time window
        recent_requests = [
            req_time for req_time in requests if req_time > window_start
        ]

        return max(0, max_requests - len(recent_requests))
