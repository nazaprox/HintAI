"""HintAI advertising reward system."""

from datetime import datetime


def can_reward(last_view: datetime | None) -> bool:
    if last_view is None:
        return True
    return (datetime.utcnow() - last_view).total_seconds() > 30


def reward_amount() -> int:
    return 2
