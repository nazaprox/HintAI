"""HintAI credit economy."""

from dataclasses import dataclass

@dataclass
class CreditAccount:
    balance: int = 20


def consume(account: CreditAccount, amount: int = 1) -> bool:
    if account.balance < amount:
        return False
    account.balance -= amount
    return True


def reward(account: CreditAccount, amount: int = 1) -> int:
    account.balance += amount
    return account.balance
