"""Credit economy for HintAI V1.

The module is intentionally storage-agnostic: the caller supplies and persists
its user record. This keeps the economy compatible with the existing user.py
and storage.py implementations.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from config import (
    PLAN_CREDITS,
    STREAK_3_DAYS,
    STREAK_3_DAYS_REWARD,
    STREAK_6_DAYS,
    STREAK_6_DAYS_REWARD,
    get_action_cost,
    is_streak_action,
)


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value or "0"))


def get_balance(user: dict) -> Decimal:
    return _decimal(user.get("credits", 0))


def set_balance(user: dict, amount: Decimal) -> Decimal:
    if amount < 0:
        raise ValueError("Le solde ne peut pas être négatif.")
    user["credits"] = str(amount.normalize())
    return amount


def can_afford(user: dict, action: str) -> bool:
    return get_balance(user) >= get_action_cost(action)


def spend(user: dict, action: str) -> Decimal:
    cost = get_action_cost(action)
    balance = get_balance(user)
    if balance < cost:
        raise ValueError("Crédits insuffisants.")
    set_balance(user, balance - cost)
    return cost


def add_credits(user: dict, amount: Decimal, reason: str = "manual") -> Decimal:
    if amount <= 0:
        raise ValueError("Le nombre de crédits doit être positif.")
    new_balance = get_balance(user) + amount
    set_balance(user, new_balance)
    history = user.setdefault("credit_history", [])
    history.append({"type": "credit", "amount": str(amount), "reason": reason})
    return new_balance


def initialize_free_account(user: dict) -> dict:
    if "plan" not in user:
        user["plan"] = "free"
    if "credits" not in user:
        user["credits"] = str(PLAN_CREDITS.get(user["plan"], PLAN_CREDITS["free"]))
    user.setdefault("streak", 0)
    user.setdefault("last_streak_activity", None)
    user.setdefault("streak_rewards", [])
    user.setdefault("credit_history", [])
    return user


def apply_monthly_plan_credits(user: dict, plan: str) -> Decimal:
    normalized = plan.lower()
    if normalized not in PLAN_CREDITS:
        raise ValueError("Plan inconnu.")
    user["plan"] = normalized
    amount = Decimal(str(PLAN_CREDITS[normalized]))
    set_balance(user, amount)
    user["credit_history"] = user.get("credit_history", [])
    user["credit_history"].append({"type": "subscription", "amount": str(amount), "plan": normalized})
    return amount


def _today() -> date:
    return date.today()


def register_activity(user: dict, action: str, activity_date: date | None = None) -> dict:
    if not is_streak_action(action):
        return {"streak": int(user.get("streak", 0)), "reward": Decimal("0")}

    today = activity_date or _today()
    last_raw = user.get("last_streak_activity")
    last = date.fromisoformat(last_raw) if last_raw else None

    if last == today:
        return {"streak": int(user.get("streak", 0)), "reward": Decimal("0")}

    if last == today - timedelta(days=1):
        streak = int(user.get("streak", 0)) + 1
    else:
        streak = 1

    user["streak"] = streak
    user["last_streak_activity"] = today.isoformat()

    reward = Decimal("0")
    if streak == STREAK_3_DAYS:
        reward = STREAK_3_DAYS_REWARD
    elif streak == STREAK_6_DAYS:
        reward = STREAK_6_DAYS_REWARD

    if reward:
        add_credits(user, reward, reason=f"streak_{streak}_days")
        user.setdefault("streak_rewards", []).append({"streak": streak, "amount": str(reward), "date": today.isoformat()})

    return {"streak": streak, "reward": reward}
