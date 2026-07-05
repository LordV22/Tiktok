from pathlib import Path
from typing import Dict, Any
import subprocess
import logging

from config import settings

logger = logging.getLogger(__name__)


class Validator:
    def __init__(self):
        self.config = settings.video

    def validate(self, video_path: Path) -> Dict[str, Any]:
        errors = []

        if not video_path.exists():
            return {"valid": False, "errors": ["Arquivo não existe"]}

        size = video_path.stat().st_size
        max_bytes = settings.telegram.max_file_size_mb * 1024 * 1024
        if size > max_bytes:
            errors.append(f"Arquivo muito grande: {size / 1024 / 1024:.1f}MB")

        info = self._get_info(video_path)
        if not info:
            errors.append("Não foi possível ler info do vídeo")
            return {"valid": False, "errors": errors}

        if info.get("duration", 0) > self.config.max_duration:
            errors.append(f"Duração excede limite: {info['duration']}s")

        if info.get("duration", 0) == 0:
            errors.append("Vídeo tem duração zero")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "info": info,
        }

    def _get_info(self, video_path: Path) -> Dict[str, Any]:
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration,size,bit_rate",
                "-show_entries", "stream=codec_name,width,height,r_frame_rate",
                "-of", "json",
                str(video_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return None

            import json
            data = json.loads(result.stdout)

            fmt = data.get("format", {})
            streams = data.get("streams", [])
            video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
            audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

            return {
                "duration": float(fmt.get("duration", 0)),
                "size": int(fmt.get("size", 0)),
                "bitrate": int(fmt.get("bit_rate", 0)),
                "codec": video_stream.get("codec_name", "unknown"),
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "fps": video_stream.get("r_frame_rate", "30/1"),
                "has_audio": bool(audio_stream),
            }

        except Exception as e:
            logger.error(f"Probe erro: {e}")
            return None

    def can_send_telegram(self, video_path: Path) -> bool:
        max_bytes = settings.telegram.max_file_size_mb * 1024 * 1024
        return video_path.stat().st_size <= max_bytes
