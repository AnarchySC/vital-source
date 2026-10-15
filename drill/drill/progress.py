"""Progress lives outside the sandbox home so --reset and rm -rf ~ can't take it."""

import json
import os
from pathlib import Path


def default_dir() -> Path:
    env = os.environ.get("DRILL_HOME")
    if env:
        return Path(env)
    shared = Path("/var/lib/drill")
    if shared.is_dir() and os.access(shared, os.W_OK):
        return shared
    return Path.home() / ".drill"


class Progress:
    def __init__(self, directory: Path = None):
        self.dir = directory or default_dir()
        self.path = self.dir / "progress.json"
        try:
            self.data = json.loads(self.path.read_text())
        except (OSError, ValueError):
            self.data = {}
        self.data.setdefault("exercises", {})
        self.data.setdefault("intro_seen", [])
        self.data.setdefault("current", None)

    def ex(self, ex_id: str) -> dict:
        rec = self.data["exercises"].setdefault(ex_id, {})
        for k, v in (("reps", 0), ("passes", 0), ("streak", 0), ("mastered", False), ("best", None)):
            rec.setdefault(k, v)
        return rec

    def save(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=1))
        os.replace(tmp, self.path)
