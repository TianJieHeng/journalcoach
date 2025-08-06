# -*- coding: utf-8 -*-
import time
from typing import Callable, TypeVar

T = TypeVar("T")

def retry(fn: Callable[[], T], attempts: int = 3, base_delay: float = 0.5) -> T:
    last_exc = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            time.sleep(base_delay * (2 ** i))
    raise last_exc
