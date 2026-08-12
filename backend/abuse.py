from collections import defaultdict
from time import time

_requests = defaultdict(list)


def allowed(identifier: str, limit: int = 20) -> bool:
    now = time()
    _requests[identifier] = [t for t in _requests[identifier] if now - t < 60]
    if len(_requests[identifier]) >= limit:
        return False
    _requests[identifier].append(now)
    return True


def check_rate_limit(identifier: str) -> bool:
    return allowed(identifier, 30)
