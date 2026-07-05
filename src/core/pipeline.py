from moviepy.editor import (
    ColorClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, VideoFileClip, AudioFileClip,
)
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import time

from config import settings
from .render import Renderer
from .validator import Validator

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self):
        self.renderer = Renderer()
        self.validator = Validator()

    def create_from_ai(
        self,
        video_data: Dict[str, Any],
        output_path: Path,
        images: Optional[List[Path]] = None,
    ) -> Dict[str, Any]:
        start = time.time()

        try:
            scenes = video_data.get("scenes", [])
            resolution = tuple(video_data.get("resolution", [1920, 1080]))
            duration = video_data.get("duration", 15)

            clips = self._build_scenes(scenes, resolution, images)

            if not clips:
                return {"success": False, "error": "Nenhuma cena criada"}

            video = concatenate_videoclips(clips, method="compose")

            effects = video_data.get("effects", [])
            video = self._apply_effects(video, effects)

            result = self.renderer.render(video, output_path)

            video.close()

            if result["success"]:
                self.validator.validate(output_path)

            result["processing_time"] = time.time() - start
            return result

        except Exception as e:
            logger.error(f"Pipeline erro: {e}")
            return {"success": False, "error": str(e)}

    def merge_videos(
        self,
        paths: List[Path],
        output_path: Path,
        transition: str = "fade",
    ) -> Dict[str, Any]:
        try:
            clips = []
            for p in paths:
                clip = VideoFileClip(str(p))
                clips.append(clip)

            if len(clips) > 1 and transition == "fade":
                from moviepy.video.compositing.transitions import crossfadein
                for i in range(1, len(clips)):
                    clips[i] = crossfadein(clips[i], 0.5)

            video = concatenate_videoclips(clips, method="compose")
            result = self.renderer.render(video, output_path)
            video.close()

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _build_scenes(
        self,
        scenes: List[Dict],
        resolution: tuple,
        images: Optional[List[Path]] = None,
    ) -> List:
        clips = []
        for i, scene in enumerate(scenes):
            clip = self._create_clip(scene, resolution, images, i)
            clips.append(clip)
        return clips

    def _create_clip(self, scene: Dict, resolution: tuple, images: Optional[List[Path]], index: int):
        bg = scene.get("bg_color", [20, 40, 80])
        start = scene.get("start", 0)
        end = scene.get("end", 5)
        duration = end - start

        if images and index < len(images):
            from moviepy.editor import ImageClip
            clip = ImageClip(str(images[index % len(images)]), duration=duration)
            clip = clip.resize(resolution)
        else:
            clip = ColorClip(size=resolution, color=tuple(bg), duration=duration)

        text = scene.get("text")
        if text:
            text_size = scene.get("text_size", 60)
            text_color = scene.get("text_color", "white")
            text_pos = scene.get("text_pos", "center")

            txt = TextClip(
                text, fontsize=text_size, color=text_color,
                font="Arial", stroke_color="black", stroke_width=3,
            )

            pos_map = {"center": "center", "top": ("center", 50), "bottom": ("center", "bottom")}
            txt = txt.set_position(pos_map.get(text_pos, "center"))
            txt = txt.set_duration(duration)

            clip = CompositeVideoClip([clip, txt])

        return clip

    def _apply_effects(self, video, effects: list):
        from moviepy.video.fx.all import fadein, fadeout

        for effect in effects:
            if effect == "fade_in":
                video = fadein(video, 1.0)
            elif effect == "fade_out":
                video = fadeout(video, 1.0)

        return video
