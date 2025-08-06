# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv, find_dotenv

def load_env() -> None:
    # Find .env by walking up from the current working directory.
    # This makes launching from either the project root or src work the same.
    path = find_dotenv(usecwd=True)
    load_dotenv(dotenv_path=path, override=False)

def get_model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

def get_api_key() -> str:
    return os.environ.get("OPENAI_API_KEY", "")

def get_rate_limit_per_minute() -> int:
    try:
        return int(os.environ.get("RATE_LIMIT_PER_MINUTE", "30"))
    except ValueError:
        return 30
