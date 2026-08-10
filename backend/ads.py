"""HintAI V2 advertising rules."""

from __future__ import annotations

from datetime import datetime, timezone

from config import (
    MAX_DAILY_REWARDED_ADS,
    REWARDED_AD_CREDITS,
    REWARDED_AD_DURATION_SECONDS,
    SIMPLE_AD_DURATION_SECONDS,
    SIMPLE_AD_REWARD_CREDITS,
)


def can_reward(last_view: datetime | None, daily_count: int = 0) -> bool:
    """Return whether a rewarded ad can currently grant credits."""
    if daily_count >= MAX_DAILY_REWARDED_ADS:
        return False
    if last_view is None:
        return True
    if last_view.tzinfo is None:
        last_view = last_view.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - last_view).total_seconds() >= REWARDED_AD_DURATION_SECONDS


def simple_ad_duration() -> int:
    return SIMPLE_AD_DURATION_SECONDS


def simple_ad_reward() -> int:
    return int(SIMPLE_AD_REWARD_CREDITS)


def rewarded_ad_duration() -> int:
    return REWARDED_AD_DURATION_SECONDS


def reward_amount() -> int:
    return int(REWARDED_AD_CREDITS)
