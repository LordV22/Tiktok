from moviepy.editor import (
    ColorClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, VideoClip, AudioFileClip,
)
import numpy as np
import cv2
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import time
import subprocess
import json

from config import settings
from .render import Renderer
from .validator import Validator

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self):
        self.renderer = Renderer()
        self.validator = Validator()
        self._effects = None
        self._cinematic = None
        self._color_grading = None
        self._transitions = None
        self._particles = None
        self._overlays = None

    @property
    def effects(self):
        if self._effects is None:
            from src.effects.cinematic import CinematicEffects
            self._effects = CinematicEffects()
        return self._effects

    @property
    def cinematic(self):
        if self._cinematic is None:
            from src.effects.cinematic import CinematicEffects
            self._cinematic = CinematicEffects()
        return self._cinematic

    @property
    def color_grading(self):
        if self._color_grading is None:
            from src.effects.color_grading import ColorGrading
            self._color_grading = ColorGrading()
        return self._color_grading

    @property
    def transitions(self):
        if self._transitions is None:
            from src.effects.transitions import Transitions
            self._transitions = Transitions()
        return self._transitions

    @property
    def particles(self):
        if self._particles is None:
            from src.effects.particles import ParticleEffects
            self._particles = ParticleEffects()
        return self._particles

    @property
    def overlays(self):
        if self._overlays is None:
            from src.effects.overlays import OverlayEffects
            self._overlays = OverlayEffects()
        return self._overlays

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
            color_grading_name = video_data.get("color_grading", "cinematic")
            transitions_list = video_data.get("transitions", ["fade"])
            audio_config = video_data.get("audio", {})

            if not scenes:
                return {"success": False, "error": "Nenhuma cena definida"}

            scene_clips = []
            for i, scene in enumerate(scenes):
                clip = self._build_scene(scene, resolution, images, i)
                scene_clips.append(clip)

            if len(scene_clips) > 1:
                video = self._apply_transitions(scene_clips, transitions_list)
            else:
                video = scene_clips[0]

            video = self._apply_color_grading(video, color_grading_name)

            audio_path = self._generate_audio(audio_config, duration)
            if audio_path and audio_path.exists():
                try:
                    audio_clip = AudioFileClip(str(audio_path))
                    if audio_clip.duration > duration:
                        audio_clip = audio_clip.subclip(0, duration)
                    elif audio_clip.duration < duration:
                        loops = int(duration / audio_clip.duration) + 1
                        from moviepy.editor import concatenate_audioclips
                        audio_clip = concatenate_audioclips([audio_clip] * loops)
                        audio_clip = audio_clip.subclip(0, duration)
                    video = video.set_audio(audio_clip)
                except Exception as e:
                    logger.warning(f"Erro ao adicionar áudio: {e}")

            result = self.renderer.render(video, output_path)

            video.close()

            if result["success"]:
                try:
                    self.validator.validate(output_path)
                except Exception:
                    pass

            result["processing_time"] = time.time() - start
            return result

        except Exception as e:
            logger.error(f"Pipeline erro: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _build_scene(
        self,
        scene: Dict,
        resolution: tuple,
        images: Optional[List[Path]],
        index: int,
    ) -> VideoClip:
        w, h = resolution
        bg_color = scene.get("bg_color", [20, 40, 80])
        start = scene.get("start", 0)
        end = scene.get("end", 5)
        duration = end - start

        if duration <= 0:
            duration = 3

        if images and index < len(images):
            from moviepy.editor import ImageClip
            clip = ImageClip(str(images[index % len(images)]), duration=duration)
            clip = clip.resize(resolution)
        else:
            clip = ColorClip(size=resolution, color=tuple(bg_color), duration=duration)

        clip = clip.set_fps(30)

        cinematic_effect = scene.get("cinematic_effect", "none")
        if cinematic_effect and cinematic_effect != "none":
            clip = self._apply_cinematic_effect(clip, cinematic_effect)

        text = scene.get("text")
        if text:
            text_overlay = self._create_text_overlay(
                text=text,
                subtitle=scene.get("subtitle", ""),
                duration=duration,
                resolution=resolution,
                position=scene.get("text_pos", "center"),
                font_size=scene.get("text_size", 60),
                text_color=scene.get("text_color", "white"),
                animation=scene.get("text_animation", "fade"),
            )
            if text_overlay is not None:
                clip = CompositeVideoClip([clip, text_overlay], size=resolution)

        particle_type = scene.get("particle", "none")
        if particle_type and particle_type != "none":
            clip = self._apply_particle(clip, particle_type)

        overlay_type = scene.get("overlay", "none")
        if overlay_type and overlay_type != "none":
            clip = self._apply_overlay(clip, overlay_type)

        clip = clip.set_duration(duration)
        return clip

    def _create_text_overlay(
        self,
        text: str,
        subtitle: str,
        duration: float,
        resolution: tuple,
        position: str,
        font_size: int,
        text_color: str,
        animation: str,
    ) -> VideoClip:
        w, h = resolution

        pos_map = {
            "center": ("center", "center"),
            "top": ("center", str(int(h * 0.3))),
            "bottom": ("center", str(int(h * 0.7))),
        }
        pos = pos_map.get(position, ("center", "center"))

        if animation == "typewriter":
            return self._animate_typewriter(text, duration, resolution, position, font_size, text_color)

        try:
            txt = TextClip(
                text,
                fontsize=font_size,
                color=text_color,
                font="Liberation-Sans",
                stroke_color="black",
                stroke_width=2,
            )
        except Exception:
            txt = TextClip(
                text,
                fontsize=font_size,
                color=text_color,
                stroke_color="black",
                stroke_width=2,
            )

        txt = txt.set_position(pos)
        txt = txt.set_duration(duration)

        if animation == "fade":
            fade_dur = min(0.8, duration * 0.25)
            txt = txt.crossfadein(fade_dur).crossfadeout(fade_dur)
        elif animation == "slide":
            start_x = -txt.size[0] if txt.size else -200
            txt = txt.set_position(lambda t, sx=start_x: (
                sx + (w - sx) * min(t / 1.0, 1.0),
                txt.get_position(t)[1] if isinstance(txt.get_position(t), tuple) else "center"
            ))
        elif animation == "bounce":
            base_y = int(pos[1]) if pos[1] != "center" else h // 2
            txt = txt.set_position(lambda t: (
                txt.get_position(t)[0] if isinstance(txt.get_position(t), tuple) else "center",
                base_y - int(abs(np.sin(t * 4)) * 30)
            ))
        elif animation == "wave":
            base_y = int(pos[1]) if pos[1] != "center" else h // 2
            txt = txt.set_position(lambda t: (
                txt.get_position(t)[0] if isinstance(txt.get_position(t), tuple) else "center",
                base_y + int(10 * np.sin(t * 5))
            ))

        if subtitle:
            try:
                sub = TextClip(
                    subtitle,
                    fontsize=max(24, font_size // 2),
                    color="white",
                    font="Liberation-Sans",
                    stroke_color="black",
                    stroke_width=1,
                )
            except Exception:
                sub = TextClip(
                    subtitle,
                    fontsize=max(24, font_size // 2),
                    color="white",
                    stroke_color="black",
                    stroke_width=1,
                )
            sub_y = int(h * 0.6) if position == "center" else int(h * 0.75)
            sub = sub.set_position(("center", sub_y))
            sub = sub.set_duration(duration)
            sub = sub.crossfadein(0.5)
            return CompositeVideoClip([txt, sub], size=resolution)

        return txt

    def _animate_typewriter(
        self, text: str, duration: float, resolution: tuple,
        position: str, font_size: int, text_color: str,
    ) -> VideoClip:
        try:
            txt = TextClip(
                text,
                fontsize=font_size,
                color=text_color,
                font="Liberation-Sans",
                stroke_color="black",
                stroke_width=2,
            )
        except Exception:
            txt = TextClip(
                text,
                fontsize=font_size,
                color=text_color,
                stroke_color="black",
                stroke_width=2,
            )

        pos_map = {
            "center": ("center", "center"),
            "top": ("center", str(int(resolution[1] * 0.3))),
            "bottom": ("center", str(int(resolution[1] * 0.7))),
        }
        txt = txt.set_position(pos_map.get(position, ("center", "center")))
        txt = txt.set_duration(duration)
        fade_dur = min(0.3, duration * 0.1)
        txt = txt.crossfadein(fade_dur)
        return txt

    def _apply_cinematic_effect(self, clip: VideoClip, effect_name: str) -> VideoClip:
        func = self.cinematic.get(effect_name)
        if func:
            try:
                clip = func(clip)
            except Exception as e:
                logger.warning(f"Efeito cinemático {effect_name} falhou: {e}")
        return clip

    def _apply_particle(self, clip: VideoClip, particle_type: str) -> VideoClip:
        try:
            if particle_type == "snow":
                clip = self.particles.snow(clip, count=100)
            elif particle_type == "rain":
                clip = self.particles.rain(clip, count=200)
            elif particle_type == "sparkles":
                clip = self.particles.sparkles(clip, count=50)
            elif particle_type == "bubbles":
                clip = self.particles.bubbles(clip, count=30)
            elif particle_type == "confetti":
                clip = self.particles.confetti(clip, count=100)
        except Exception as e:
            logger.warning(f"Partícula {particle_type} falhou: {e}")
        return clip

    def _apply_overlay(self, clip: VideoClip, overlay_type: str) -> VideoClip:
        try:
            if overlay_type == "scan_lines":
                clip = self.overlays.scan_lines(clip)
            elif overlay_type == "bokeh":
                clip = self.overlays.bokeh(clip)
            elif overlay_type == "lens_flare":
                clip = self.overlays.lens_flare(clip)
            elif overlay_type == "film_grain":
                clip = self.overlays.film_grain(clip)
        except Exception as e:
            logger.warning(f"Overlay {overlay_type} falhou: {e}")
        return clip

    def _apply_transitions(self, clips: List[VideoClip], transitions_list: List) -> VideoClip:
        if len(clips) < 2:
            return clips[0]

        result = clips[0]
        for i in range(1, len(clips)):
            transition_name = transitions_list[(i - 1) % len(transitions_list)] if transitions_list else "fade"
            transition_dur = min(0.5, clips[i].duration * 0.15)

            try:
                trans_func = self.transitions.get(transition_name)
                result = trans_func(result, clips[i], transition_dur)
            except Exception as e:
                logger.warning(f"Transição {transition_name} falhou: {e}")
                result = concatenate_videoclips([result, clips[i]], method="compose")

        return result

    def _apply_color_grading(self, video: VideoClip, grading_name: str) -> VideoClip:
        if not grading_name or grading_name == "none":
            return video
        try:
            video = self.color_grading.apply(video, grading_name, intensity=0.6)
        except Exception as e:
            logger.warning(f"Color grading {grading_name} falhou: {e}")
        return video

    def _generate_audio(self, audio_config: Dict, duration: float) -> Optional[Path]:
        if not audio_config.get("enabled", False):
            return None

        mood = audio_config.get("mood", "calm")
        volume = audio_config.get("volume", 0.7)

        try:
            import wave
            sample_rate = 44100
            num_samples = int(duration * sample_rate)
            t = np.linspace(0, duration, num_samples, False)

            freq_map = {
                "upbeat": [220, 277, 330, 440],
                "calm": [174, 220, 261, 329],
                "dramatic": [130, 164, 196, 261],
                "epic": [110, 146, 164, 220],
                "chill": [196, 233, 293, 349],
                "intense": [146, 174, 220, 293],
            }

            freqs = freq_map.get(mood, [220, 277, 330, 440])
            audio = np.zeros(num_samples)

            for i, freq in enumerate(freqs):
                harmonics = [1, 0.5, 0.25, 0.125]
                for h_idx, amp in enumerate(harmonics):
                    audio += amp * np.sin(2 * np.pi * freq * (h_idx + 1) * t) / len(freqs)

            envelope = np.ones(num_samples)
            fade_samples = min(int(0.5 * sample_rate), num_samples // 4)
            if fade_samples > 0:
                envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
                envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
            audio *= envelope * volume

            audio_int = (audio * 32767).astype(np.int16)

            temp_audio = Path(settings.paths.temp) / "generated_audio.wav"
            temp_audio.parent.mkdir(parents=True, exist_ok=True)

            with wave.open(str(temp_audio), 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_int.tobytes())

            return temp_audio

        except Exception as e:
            logger.warning(f"Geração de áudio falhou: {e}")
            return None

    def merge_videos(self, paths: List[Path], output_path: Path, transition: str = "fade") -> Dict[str, Any]:
        try:
            clips = [VideoClip(str(p)) for p in paths]
            video = self._apply_transitions(clips, [transition])
            result = self.renderer.render(video, output_path)
            video.close()
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
