"""Advertisement and rewarded-credit rules for HintAI V1."""

from __future__ import annotations

from datetime import date

from config import (
    MAX_DAILY_REWARDED_ADS,
    REWARDED_AD_CREDITS,
    REWARDED_AD_DURATION_SECONDS,
    SIMPLE_AD_DURATION_SECONDS,
    SIMPLE_AD_REWARD_CREDITS,
)
from credits import add_credits


def simple_ad() -> dict:
    return {
        "type": "simple",
        "durationSeconds": SIMPLE_AD_DURATION_SECONDS,
        "rewardCredits": str(SIMPLE_AD_REWARD_CREDITS),
        "rewarded": False,
    }


def _rewarded_count(user: dict) -> int:
    today = date.today().isoformat()
    return sum(
        1
        for item in user.get("ad_history", [])
        if item.get("type") == "rewarded" and item.get("date") == today
    )


def rewarded_status(user: dict) -> dict:
    used = _rewarded_count(user)
    return {
        "available": used < MAX_DAILY_REWARDED_ADS,
        "usedToday": used,
        "dailyLimit": MAX_DAILY_REWARDED_ADS,
        "durationSeconds": REWARDED_AD_DURATION_SECONDS,
        "rewardCredits": str(REWARDED_AD_CREDITS),
    }


def claim_rewarded_ad(user: dict) -> dict:
    status = rewarded_status(user)
    if not status["available"]:
        raise ValueError("Limite quotidienne de publicités récompensées atteinte.")

    today = date.today().isoformat()
    user.setdefault("ad_history", []).append({
        "type": "rewarded",
        "date": today,
        "durationSeconds": REWARDED_AD_DURATION_SECONDS,
        "rewardCredits": str(REWARDED_AD_CREDITS),
    })
    balance = add_credits(user, REWARDED_AD_CREDITS, reason="rewarded_ad")

    return {
        "success": True,
        "rewardCredits": str(REWARDED_AD_CREDITS),
        "balance": str(balance),
        "status": rewarded_status(user),
    }
