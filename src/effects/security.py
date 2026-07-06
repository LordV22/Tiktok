import numpy as np
from moviepy.editor import VideoClip, CompositeVideoClip
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Watermark:
    def __init__(self):
        pass

    def add_text(
        self,
        clip: VideoClip,
        text: str,
        position: str = "bottom-right",
        opacity: float = 0.5,
        font_size: int = 24,
    ) -> VideoClip:
        from moviepy.editor import TextClip

        txt = TextClip(
            text,
            fontsize=font_size,
            color="white",
            font="Arial",
            bg_color="rgba(0,0,0,0.5)",
        )

        pos_map = {
            "top-left": (10, 10),
            "top-right": ("center", 10),
            "bottom-left": (10, "bottom"),
            "bottom-right": ("center", "bottom"),
            "center": "center",
        }

        txt = txt.set_position(pos_map.get(position, "bottom-right"))
        txt = txt.set_duration(clip.duration)
        txt = txt.set_opacity(opacity)

        return CompositeVideoClip([clip, txt])

    def add_image(
        self,
        clip: VideoClip,
        image_path: Path,
        position: str = "bottom-right",
        opacity: float = 0.7,
        height: int = 50,
    ) -> VideoClip:
        from moviepy.editor import ImageClip

        img = ImageClip(str(image_path))
        img = img.resize(height=height)
        img = img.set_opacity(opacity)
        img = img.set_duration(clip.duration)

        pos_map = {
            "top-left": (10, 10),
            "top-right": ("right", 10),
            "bottom-left": (10, "bottom"),
            "bottom-right": ("right", "bottom"),
        }

        img = img.set_position(pos_map.get(position, "right", "bottom"))

        return CompositeVideoClip([clip, img])

    def add_signature(
        self,
        clip: VideoClip,
        text: str = "© VideoBot",
    ) -> VideoClip:
        return self.add_text(clip, text, position="bottom-right", opacity=0.3, font_size=16)


class SecurityEffects:
    def __init__(self):
        self.watermark = Watermark()

    def protect_video(
        self,
        clip: VideoClip,
        owner: str,
        show_watermark: bool = True,
    ) -> VideoClip:
        if show_watermark:
            clip = self.watermark.add_signature(clip, f"© {owner}")
        return clip

    def add_invisible_watermark(self, clip: VideoClip, data: str) -> VideoClip:
        def effect(get_frame, t):
            frame = get_frame(t).copy()
            bits = ''.join(format(ord(c), '08b') for c in data[:16])
            h, w = frame.shape[:2]
            idx = 0
            for i in range(0, min(len(bits), h * w // 4)):
                y = (i * 4) // w
                x = (i * 4) % w
                if y < h and x < w and idx < len(bits):
                    frame[y, x, 0] = (frame[y, x, 0] & 0xFE) | int(bits[idx])
                    idx += 1
            return frame
        return clip.fl(effect)
