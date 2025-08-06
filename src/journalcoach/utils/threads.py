# -*- coding: utf-8 -*-
import threading

def run_in_thread(target, *args, **kwargs) -> threading.Thread:
    t = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return t
