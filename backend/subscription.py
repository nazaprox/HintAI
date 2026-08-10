"""HintAI V2 subscription and credit pack helpers."""

from __future__ import annotations

from decimal import Decimal

from config import CREDIT_PACK_PRICE_USD, CREDIT_PACK_SIZE, PLAN_CREDITS, PLAN_PRICES_USD


def get_plan(plan: str) -> dict:
    key = plan.lower()
    if key not in PLAN_CREDITS:
        key = "free"
    return {
        "id": key,
        "credits": PLAN_CREDITS[key],
        "price_usd": str(PLAN_PRICES_USD[key]),
    }


def list_plans() -> list[dict]:
    return [get_plan(plan) for plan in PLAN_CREDITS]


def credit_pack(quantity: int = 1) -> dict:
    if quantity < 1:
        raise ValueError("quantity doit être supérieur ou égal à 1")
    return {
        "quantity": quantity,
        "credits": CREDIT_PACK_SIZE * quantity,
        "price_usd": str(CREDIT_PACK_PRICE_USD * Decimal(quantity)),
    }
