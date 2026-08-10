"""HintAI V2 in-process credit ledger.

This is a development ledger. A persistent database should replace it before
production so balances survive instance restarts and multiple Render workers.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from threading import Lock

from config import (
    STREAK_3_DAYS,
    STREAK_3_DAYS_REWARD,
    STREAK_6_DAYS,
    STREAK_6_DAYS_REWARD,
    get_action_cost,
    get_plan_credits,
    is_streak_action,
)

_LOCK = Lock()
_ACCOUNTS: dict[str, dict] = {}


def _account(user_id: str) -> dict:
    with _LOCK:
        if user_id not in _ACCOUNTS:
            _ACCOUNTS[user_id] = {
                "userId": user_id,
                "plan": "free",
                "balance": Decimal(get_plan_credits("free")),
                "streak": 0,
                "lastActionDate": None,
                "reward3Claimed": False,
                "reward6Claimed": False,
                "transactions": [],
            }
        return _ACCOUNTS[user_id]


def get_account(user_id: str) -> dict:
    account = _account(user_id)
    with _LOCK:
        return {
            **account,
            "balance": float(account["balance"]),
            "transactions": list(account["transactions"]),
        }


def set_plan(user_id: str, plan: str) -> dict:
    account = _account(user_id)
    with _LOCK:
        account["plan"] = plan.lower()
        account["balance"] = Decimal(get_plan_credits(plan))
        account["transactions"].append({"type": "plan", "plan": account["plan"], "amount": float(account["balance"])})
    return get_account(user_id)


def consume(user_id: str, action: str) -> dict:
    amount = Decimal(get_action_cost(action))
    account = _account(user_id)
    with _LOCK:
        if account["balance"] < amount:
            raise ValueError("Crédits insuffisants.")
        account["balance"] -= amount
        account["transactions"].append({"type": "spend", "action": action, "amount": -float(amount), "balance": float(account["balance"])})
    return get_account(user_id)


def reward(user_id: str, amount: int | Decimal, reason: str = "reward") -> dict:
    account = _account(user_id)
    value = Decimal(amount)
    if value <= 0:
        raise ValueError("La récompense doit être positive.")
    with _LOCK:
        account["balance"] += value
        account["transactions"].append({"type": "reward", "reason": reason, "amount": float(value), "balance": float(account["balance"])})
    return get_account(user_id)


def register_action(user_id: str, action: str) -> dict:
    """Register one real educational action and update the streak once/day."""
    if not is_streak_action(action):
        return get_account(user_id)

    account = _account(user_id)
    today = date.today()
    with _LOCK:
        last = account["lastActionDate"]
        if last == today.isoformat():
            return get_account(user_id)

        if last:
            try:
                last_date = date.fromisoformat(last)
            except ValueError:
                last_date = None
        else:
            last_date = None

        if last_date == today - timedelta(days=1):
            account["streak"] += 1
        else:
            account["streak"] = 1

        account["lastActionDate"] = today.isoformat()

        if account["streak"] >= STREAK_6_DAYS and not account["reward6Claimed"]:
            account["balance"] += STREAK_6_DAYS_REWARD
            account["reward6Claimed"] = True
            account["transactions"].append({"type": "reward", "reason": "streak_6_days", "amount": float(STREAK_6_DAYS_REWARD)})
        elif account["streak"] >= STREAK_3_DAYS and not account["reward3Claimed"]:
            account["balance"] += STREAK_3_DAYS_REWARD
            account["reward3Claimed"] = True
            account["transactions"].append({"type": "reward", "reason": "streak_3_days", "amount": float(STREAK_3_DAYS_REWARD)})

    return get_account(user_id)
