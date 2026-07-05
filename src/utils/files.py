from pathlib import Path
from typing import Optional, List
import time
import hashlib
import shutil
import os


class FileManager:
    def __init__(self, temp_dir: Path, output_dir: Path):
        self.temp = temp_dir
        self.output = output_dir
        self.temp.mkdir(parents=True, exist_ok=True)
        self.output.mkdir(parents=True, exist_ok=True)

    def temp_path(self, prefix: str, ext: str) -> Path:
        ts = int(time.time() * 1000)
        h = hashlib.md5(f"{prefix}_{ts}".encode()).hexdigest()[:8]
        return self.temp / f"{prefix}_{h}.{ext}"

    def output_path(self, prefix: str, ext: str = "mp4") -> Path:
        ts = int(time.time() * 1000)
        h = hashlib.md5(f"{prefix}_{ts}".encode()).hexdigest()[:8]
        return self.output / f"{prefix}_{h}.{ext}"

    def safe_delete(self, path: Optional[Path]):
        if path and path.exists():
            try:
                path.unlink()
            except Exception:
                pass

    def cleanup_temp(self, max_age_hours: int = 24):
        now = time.time()
        for f in self.temp.glob("*"):
            if f.is_file():
                age = now - f.stat().st_mtime
                if age > max_age_hours * 3600:
                    f.unlink()

    def get_size(self, path: Path) -> str:
        size = path.stat().st_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def safe_save(self, data: bytes, path: Path) -> bool:
        try:
            tmp = path.with_suffix(".tmp")
            tmp.write_bytes(data)
            tmp.rename(path)
            return True
        except Exception:
            return False

    def copy(self, src: Path, dst: Path) -> bool:
        try:
            shutil.copy2(src, dst)
            return True
        except Exception:
            return False

    def list_files(self, directory: Path, pattern: str = "*") -> List[Path]:
        return sorted(directory.glob(pattern), key=lambda f: f.stat().st_mtime, reverse=True)
