# -*- coding: utf-8 -*-
import time
from collections import deque

class TokenBucket:
    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self.events = deque()

    def allow(self) -> bool:
        now = time.time()
        cutoff = now - 60.0
        while self.events and self.events[0] < cutoff:
            self.events.popleft()
        if len(self.events) < self.max_per_minute:
            self.events.append(now)
            return True
        return False
