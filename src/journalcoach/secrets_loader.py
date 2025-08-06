# -*- coding: utf-8 -*-
"""
Dev: reads OPENAI_API_KEY from .env via config.env.load_env().
Prod packaging plan (Windows-only suggestion):
- Encrypt your API key with DPAPI (user scope) and embed the blob as a constant.
- At runtime, decrypt and set os.environ['OPENAI_API_KEY'] before creating the client.
This avoids storing the key in plain text on disk. The EXE is for private use only.
"""
import os

ENCRYPTED_KEY_B64 = ""  # optional DPAPI-encrypted blob for packaging later

def set_api_key_from_embedded_blob_if_available() -> None:
    if ENCRYPTED_KEY_B64:
        # TODO: decrypt and set os.environ["OPENAI_API_KEY"]
        pass
