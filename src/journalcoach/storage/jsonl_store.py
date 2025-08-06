# -*- coding: utf-8 -*-
import json
import os
import shutil
from datetime import datetime, timezone
from typing import Dict, Iterable, Optional

class JSONLStore:
    def __init__(self, path: Optional[str]) -> None:
        self.path = path

    def set_path(self, path: str) -> None:
        self.path = path

    def ensure_file(self) -> None:
        if not self.path:
            raise ValueError("No JSONL path set.")
        folder = os.path.dirname(self.path) or "."
        os.makedirs(folder, exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                pass

    def backup(self) -> None:
        if not self.path:
            return
        if os.path.exists(self.path):
            shutil.copy2(self.path, self.path + ".bak")

    def append_entry(self, data: Dict) -> None:
        self.ensure_file()
        self.backup()
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def load_all(self) -> Iterable[Dict]:
        if not self.path or not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except Exception:
                        continue

def build_record(title: str, summary: str) -> Dict:
    now_local = datetime.now()
    now_gmt = datetime.now(timezone.utc)
    return {
        "date_local": now_local.strftime("%Y-%m-%d"),
        "time_gmt_iso": now_gmt.isoformat(),
        "title": title,
        "summary": summary,
    }
