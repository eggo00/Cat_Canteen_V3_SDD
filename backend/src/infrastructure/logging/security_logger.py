"""Security logging for authentication and authorization events.

Logs security-related events for monitoring and auditing purposes.
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from src.infrastructure.config import settings


class SecurityEventType(str, Enum):
    """Types of security events."""

    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"
    TOKEN_REFRESH = "TOKEN_REFRESH"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"


@dataclass
class SecurityEvent:
    """Security event data."""

    event_type: SecurityEventType
    timestamp: datetime
    ip_address: str | None
    user_id: str | None
    email: str | None
    details: dict[str, Any] | None


class SecurityLogger:
    """Security event logger.

    Logs authentication failures, permission denials, and other security events.
    In production, this could be extended to send to SIEM or security monitoring.
    """

    def __init__(self) -> None:
        """Initialize security logger."""
        self._logger = logging.getLogger("security")
        self._configure_logger()

    def _configure_logger(self) -> None:
        """Configure the security logger."""
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - SECURITY - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(
                logging.DEBUG if settings.DEBUG else logging.INFO
            )

    def log_event(self, event: SecurityEvent) -> None:
        """Log a security event.

        Args:
            event: Security event to log
        """
        message = self._format_event(event)

        if event.event_type in (
            SecurityEventType.LOGIN_FAILURE,
            SecurityEventType.PERMISSION_DENIED,
            SecurityEventType.TOKEN_INVALID,
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            SecurityEventType.ACCOUNT_LOCKED,
        ) or event.event_type == SecurityEventType.RATE_LIMIT_EXCEEDED:
            self._logger.warning(message)
        else:
            self._logger.info(message)

    def _format_event(self, event: SecurityEvent) -> str:
        """Format security event for logging.

        Args:
            event: Security event

        Returns:
            Formatted log message
        """
        parts = [
            f"[{event.event_type.value}]",
            f"IP={event.ip_address or 'unknown'}",
        ]

        if event.user_id:
            parts.append(f"user_id={event.user_id}")
        if event.email:
            # Mask email for privacy
            parts.append(f"email={self._mask_email(event.email)}")
        if event.details:
            details_str = ", ".join(f"{k}={v}" for k, v in event.details.items())
            parts.append(f"details=({details_str})")

        return " ".join(parts)

    def _mask_email(self, email: str) -> str:
        """Mask email for privacy in logs.

        Args:
            email: Email address to mask

        Returns:
            Masked email (e.g., j***@example.com)
        """
        if "@" not in email:
            return "***"
        local, domain = email.split("@", 1)
        if len(local) <= 1:
            return f"*@{domain}"
        return f"{local[0]}***@{domain}"

    def log_login_success(
        self,
        email: str,
        user_id: str,
        ip_address: str | None = None,
    ) -> None:
        """Log successful login.

        Args:
            email: User email
            user_id: User ID
            ip_address: Client IP address
        """
        self.log_event(
            SecurityEvent(
                event_type=SecurityEventType.LOGIN_SUCCESS,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_id=user_id,
                email=email,
                details=None,
            )
        )

    def log_login_failure(
        self,
        email: str,
        ip_address: str | None = None,
        reason: str = "Invalid credentials",
    ) -> None:
        """Log failed login attempt.

        Args:
            email: Attempted email
            ip_address: Client IP address
            reason: Failure reason
        """
        self.log_event(
            SecurityEvent(
                event_type=SecurityEventType.LOGIN_FAILURE,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_id=None,
                email=email,
                details={"reason": reason},
            )
        )

    def log_permission_denied(
        self,
        user_id: str | None,
        email: str | None,
        resource: str,
        action: str,
        ip_address: str | None = None,
    ) -> None:
        """Log permission denied event.

        Args:
            user_id: User ID (if authenticated)
            email: User email (if authenticated)
            resource: Resource that was denied
            action: Action that was denied
            ip_address: Client IP address
        """
        self.log_event(
            SecurityEvent(
                event_type=SecurityEventType.PERMISSION_DENIED,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_id=user_id,
                email=email,
                details={"resource": resource, "action": action},
            )
        )

    def log_token_expired(
        self,
        user_id: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        """Log token expiration event.

        Args:
            user_id: User ID from expired token
            ip_address: Client IP address
        """
        self.log_event(
            SecurityEvent(
                event_type=SecurityEventType.TOKEN_EXPIRED,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_id=user_id,
                email=None,
                details=None,
            )
        )

    def log_rate_limit_exceeded(
        self,
        ip_address: str | None = None,
        endpoint: str | None = None,
    ) -> None:
        """Log rate limit exceeded event.

        Args:
            ip_address: Client IP address
            endpoint: Endpoint that was rate limited
        """
        self.log_event(
            SecurityEvent(
                event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_id=None,
                email=None,
                details={"endpoint": endpoint} if endpoint else None,
            )
        )


# Global security logger instance
_security_logger: SecurityLogger | None = None


def get_security_logger() -> SecurityLogger:
    """Get global security logger instance.

    Returns:
        Global SecurityLogger instance
    """
    global _security_logger
    if _security_logger is None:
        _security_logger = SecurityLogger()
    return _security_logger
