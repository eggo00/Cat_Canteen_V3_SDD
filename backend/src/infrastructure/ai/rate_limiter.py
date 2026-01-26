"""AI API rate limiting and cost protection.

Provides multi-level rate limiting for AI API usage:
- Per-brand daily limits
- Per-user hourly limits
- Global requests-per-minute limits

Uses in-memory storage for simplicity. For production with multiple
instances, consider using Redis.
"""
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from src.infrastructure.config import settings


@dataclass
class UsageRecord:
    """Record of API usage for rate limiting."""

    count: int = 0
    reset_at: datetime = field(default_factory=datetime.utcnow)


class AIRateLimiter:
    """Rate limiter for AI API usage.

    Implements three-level rate limiting:
    1. Per-brand daily limit (default: 50 requests/day)
    2. Per-user hourly limit (default: 10 requests/hour)
    3. Global RPM limit (default: 30 requests/minute)
    """

    def __init__(
        self,
        daily_limit_per_brand: int = 50,
        hourly_limit_per_user: int = 10,
        global_rpm_limit: int = 30,
    ):
        """Initialize rate limiter.

        Args:
            daily_limit_per_brand: Max requests per brand per day
            hourly_limit_per_user: Max requests per user per hour
            global_rpm_limit: Max requests globally per minute
        """
        # Use settings if available
        self.daily_limit_per_brand = getattr(
            settings, "AI_DAILY_LIMIT_PER_BRAND", daily_limit_per_brand
        )
        self.hourly_limit_per_user = getattr(
            settings, "AI_HOURLY_LIMIT_PER_USER", hourly_limit_per_user
        )
        self.global_rpm_limit = getattr(
            settings, "AI_GLOBAL_RPM_LIMIT", global_rpm_limit
        )

        # In-memory storage (use Redis in production for multi-instance)
        self._brand_usage: dict[str, UsageRecord] = defaultdict(UsageRecord)
        self._user_usage: dict[str, UsageRecord] = defaultdict(UsageRecord)
        self._global_usage = UsageRecord()

    def check_and_consume(
        self,
        brand_id: str,
        user_id: str,
    ) -> tuple[bool, Optional[str]]:
        """Check rate limits and consume quota if allowed.

        Args:
            brand_id: Brand identifier
            user_id: User identifier

        Returns:
            Tuple of (allowed: bool, error_message: str | None)
        """
        now = datetime.utcnow()

        # Check global RPM limit
        allowed, message = self._check_global_limit(now)
        if not allowed:
            return False, message

        # Check brand daily limit
        allowed, message = self._check_brand_limit(brand_id, now)
        if not allowed:
            return False, message

        # Check user hourly limit
        allowed, message = self._check_user_limit(user_id, now)
        if not allowed:
            return False, message

        # All checks passed, consume quota
        self._consume(brand_id, user_id, now)
        return True, None

    def get_remaining_quota(
        self,
        brand_id: str,
        user_id: str,
    ) -> dict[str, int]:
        """Get remaining quota for brand and user.

        Args:
            brand_id: Brand identifier
            user_id: User identifier

        Returns:
            Dict with remaining quota for each limit type
        """
        now = datetime.utcnow()

        # Reset expired records
        self._maybe_reset_brand(brand_id, now)
        self._maybe_reset_user(user_id, now)
        self._maybe_reset_global(now)

        return {
            "brand_daily_remaining": max(
                0, self.daily_limit_per_brand - self._brand_usage[brand_id].count
            ),
            "user_hourly_remaining": max(
                0, self.hourly_limit_per_user - self._user_usage[user_id].count
            ),
            "global_rpm_remaining": max(
                0, self.global_rpm_limit - self._global_usage.count
            ),
        }

    def _check_global_limit(self, now: datetime) -> tuple[bool, Optional[str]]:
        """Check global RPM limit."""
        self._maybe_reset_global(now)

        if self._global_usage.count >= self.global_rpm_limit:
            seconds_until_reset = (self._global_usage.reset_at - now).total_seconds()
            return False, f"系統忙碌中，請在 {int(seconds_until_reset)} 秒後重試"

        return True, None

    def _check_brand_limit(
        self, brand_id: str, now: datetime
    ) -> tuple[bool, Optional[str]]:
        """Check per-brand daily limit."""
        self._maybe_reset_brand(brand_id, now)

        usage = self._brand_usage[brand_id]
        if usage.count >= self.daily_limit_per_brand:
            return False, f"此品牌今日 AI 辨識次數已達上限 ({self.daily_limit_per_brand} 次)"

        # Warning at 80%
        if usage.count >= self.daily_limit_per_brand * 0.8:
            remaining = self.daily_limit_per_brand - usage.count
            # Log warning (in production, could send notification)
            pass

        return True, None

    def _check_user_limit(
        self, user_id: str, now: datetime
    ) -> tuple[bool, Optional[str]]:
        """Check per-user hourly limit."""
        self._maybe_reset_user(user_id, now)

        usage = self._user_usage[user_id]
        if usage.count >= self.hourly_limit_per_user:
            minutes_until_reset = (usage.reset_at - now).total_seconds() / 60
            return (
                False,
                f"您的 AI 辨識次數已達每小時上限，請在 {int(minutes_until_reset)} 分鐘後重試",
            )

        return True, None

    def _consume(self, brand_id: str, user_id: str, now: datetime) -> None:
        """Consume quota for all limit types."""
        self._brand_usage[brand_id].count += 1
        self._user_usage[user_id].count += 1
        self._global_usage.count += 1

    def _maybe_reset_brand(self, brand_id: str, now: datetime) -> None:
        """Reset brand usage if expired (daily reset)."""
        usage = self._brand_usage[brand_id]
        if now >= usage.reset_at:
            usage.count = 0
            # Reset at midnight UTC
            tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow += timedelta(days=1)
            usage.reset_at = tomorrow

    def _maybe_reset_user(self, user_id: str, now: datetime) -> None:
        """Reset user usage if expired (hourly reset)."""
        usage = self._user_usage[user_id]
        if now >= usage.reset_at:
            usage.count = 0
            usage.reset_at = now + timedelta(hours=1)

    def _maybe_reset_global(self, now: datetime) -> None:
        """Reset global usage if expired (per-minute reset)."""
        if now >= self._global_usage.reset_at:
            self._global_usage.count = 0
            self._global_usage.reset_at = now + timedelta(minutes=1)


# Singleton instance
_rate_limiter: Optional[AIRateLimiter] = None


def get_rate_limiter() -> AIRateLimiter:
    """Get the singleton rate limiter instance.

    Returns:
        AIRateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = AIRateLimiter()
    return _rate_limiter
