import hashlib
import secrets
import re
from pathlib import Path
from typing import Optional


class Security:
    def __init__(self):
        self.webhook_secret = self._load_secret()

    def _load_secret(self) -> str:
        secret = os.getenv("WEBHOOK_SECRET", "")
        if not secret:
            secret = secrets.token_hex(32)
        return secret

    def validate_user(self, user_id: int, allowed_users: list) -> bool:
        if not allowed_users:
            return True
        return user_id in allowed_users

    def validate_file_size(self, size_bytes: int, max_mb: int) -> bool:
        max_bytes = max_mb * 1024 * 1024
        return size_bytes <= max_bytes

    def validate_video_duration(self, duration: float, max_duration: int) -> bool:
        return 0 < duration <= max_duration

    def sanitize_filename(self, filename: str) -> str:
        filename = re.sub(r'[^\w\-_.]', '_', filename)
        filename = re.sub(r'_+', '_', filename)
        return filename[:100]

    def generate_token(self) -> str:
        return secrets.token_urlsafe(32)

    def hash_file(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def validate_json_response(self, data: dict) -> bool:
        required = ["duration", "resolution", "scenes"]
        return all(key in data for key in required)

    def clean_temp_files(self, temp_dir: Path, max_age_hours: int = 24):
        import time
        current = time.time()
        for f in temp_dir.glob("*"):
            if f.is_file():
                age = current - f.stat().st_mtime
                if age > max_age_hours * 3600:
                    f.unlink()


import os
