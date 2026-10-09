#!/usr/bin/env python3
"""
Production Rate Limiter for Nemotron 3 Ultra API
Token bucket implementation with per-user/project isolation.
"""

import time
import asyncio
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Optional
import json
from pathlib import Path


@dataclass
class TokenBucket:
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float = field(init=False)
    last_refill: float = field(init=False)
    lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def __post_init__(self):
        self.tokens = float(self.capacity)
        self.last_refill = time.monotonic()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_for(self, tokens: int = 1, max_wait: float = 60.0) -> bool:
        start = time.monotonic()
        while time.monotonic() - start < max_wait:
            if self.consume(tokens):
                return True
            time.sleep(0.1)
        return False


class RateLimiter:
    def __init__(self, config_path: Optional[Path] = None):
        self.buckets: Dict[str, TokenBucket] = {}
        self.lock = threading.Lock()
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        default = {
            "global": {"capacity": 100, "refill_rate": 2.0},  # 2 req/sec, burst 100
            "per_user": {"capacity": 20, "refill_rate": 0.5},  # 0.5 req/sec, burst 20
            "per_project": {"capacity": 50, "refill_rate": 1.0},  # 1 req/sec, burst 50
            "tokens_per_request": {"default": 1000, "max": 50000},
        }
        if config_path and config_path.exists():
            with open(config_path) as f:
                user_config = json.load(f)
            default.update(user_config)
        return default

    def _get_bucket(self, key: str, tier: str) -> TokenBucket:
        if key not in self.buckets:
            with self.lock:
                if key not in self.buckets:
                    cfg = self.config.get(tier, self.config["global"])
                    self.buckets[key] = TokenBucket(cfg["capacity"], cfg["refill_rate"])
        return self.buckets[key]

    def check_limit(self, user_id: str, project_id: str, estimated_tokens: int = 1000) -> tuple[bool, str]:
        estimated_tokens = min(estimated_tokens, self.config["tokens_per_request"]["max"])

        # Check global
        global_bucket = self._get_bucket("global", "global")
        if not global_bucket.consume(1):
            return False, "Global rate limit exceeded. Try again later."

        # Check per-user
        user_bucket = self._get_bucket(f"user:{user_id}", "per_user")
        if not user_bucket.consume(1):
            return False, "User rate limit exceeded. Slow down your requests."

        # Check per-project
        project_bucket = self._get_bucket(f"project:{project_id}", "per_project")
        if not project_bucket.consume(1):
            return False, "Project rate limit exceeded."

        # Check token budget (approximate)
        token_bucket = self._get_bucket(f"tokens:{user_id}", "global")
        if not token_bucket.consume(estimated_tokens):
            return False, f"Token budget exceeded. Estimated {estimated_tokens} tokens."

        return True, "OK"

    async def wait_for_slot(self, user_id: str, project_id: str, estimated_tokens: int = 1000, max_wait: float = 60.0) -> bool:
        while True:
            ok, msg = self.check_limit(user_id, project_id, estimated_tokens)
            if ok:
                return True
            if max_wait <= 0:
                return False
            await asyncio.sleep(0.5)
            max_wait -= 0.5


# Singleton instance
_limiter: Optional[RateLimiter] = None


def get_limiter(config_path: Optional[Path] = None) -> RateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter(config_path)
    return _limiter


if __name__ == "__main__":
    import asyncio

    limiter = get_limiter()

    # Demo
    print("Testing rate limiter...")
    for i in range(5):
        ok, msg = limiter.check_limit("user1", "project1", 500)
        print(f"Request {i+1}: {ok} - {msg}")
        time.sleep(0.1)

    print("\nBurst test (should hit limit)...")
    for i in range(25):
        ok, msg = limiter.check_limit("user2", "project1", 100)
        print(f"  {i+1}: {ok} - {msg}")