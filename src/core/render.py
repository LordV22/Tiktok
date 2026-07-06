from moviepy.editor import VideoClip
from pathlib import Path
from typing import Dict, Any
import subprocess
import logging

from config import settings

logger = logging.getLogger(__name__)


class Renderer:
    def __init__(self):
        self.config = settings.video

    def render(self, video: VideoClip, output_path: Path) -> Dict[str, Any]:
        try:
            video.write_videofile(
                str(output_path),
                fps=self.config.fps,
                codec=self.config.codec,
                audio_codec=self.config.audio_codec,
                preset=self.config.preset,
                bitrate=f"{self.config.crf}k",
                threads=4,
                logger=None,
            )

            return {
                "success": True,
                "output_path": str(output_path),
                "file_size": output_path.stat().st_size,
            }

        except Exception as e:
            logger.error(f"Render erro: {e}")
            return {"success": False, "error": str(e)}

    def render_with_ffmpeg(
        self,
        input_path: Path,
        output_path: Path,
        quality: str = "high",
    ) -> Dict[str, Any]:
        try:
            presets = {
                "draft": {"crf": 28, "preset": "ultrafast"},
                "low": {"crf": 26, "preset": "fast"},
                "medium": {"crf": 23, "preset": "medium"},
                "high": {"crf": 18, "preset": "slow"},
                "ultra": {"crf": 15, "preset": "veryslow"},
            }

            p = presets.get(quality, presets["high"])

            cmd = [
                "ffmpeg", "-y",
                "-i", str(input_path),
                "-c:v", "libx264",
                "-crf", str(p["crf"]),
                "-preset", p["preset"],
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                str(output_path),
            ]

            subprocess.run(cmd, check=True, capture_output=True)

            return {
                "success": True,
                "output_path": str(output_path),
                "file_size": output_path.stat().st_size,
            }

        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr.decode()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def compress(self, input_path: Path, output_path: Path, target_mb: float = 10) -> Dict[str, Any]:
        try:
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(input_path)],
                capture_output=True, text=True,
            )
            duration = float(probe.stdout.strip())
            target_bitrate = int((target_mb * 8 * 1024) / duration)

            cmd = [
                "ffmpeg", "-y",
                "-i", str(input_path),
                "-c:v", "libx264",
                "-b:v", f"{target_bitrate}k",
                "-pass", "2",
                "-c:a", "aac",
                "-b:a", "128k",
                str(output_path),
            ]

            subprocess.run(cmd, check=True, capture_output=True)

            return {"success": True, "output_path": str(output_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}
