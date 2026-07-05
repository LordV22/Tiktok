import numpy as np
import cv2
from moviepy.editor import VideoClip, TextClip, CompositeVideoClip
from typing import Tuple, Optional
import math


class AnimatedText:
    def __init__(self):
        pass

    def typewriter(
        self,
        text: str,
        duration: float,
        resolution: Tuple[int, int],
        position: Tuple[str, str] = ("center", "center"),
        font_size: int = 60,
        color: str = "white",
        speed: float = 0.05,
    ) -> VideoClip:
        w, h = resolution
        chars_per_frame = max(1, int(1 / speed / 30))

        def effect(get_frame, t):
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            visible_chars = min(len(text), int(t / speed))
            visible_text = text[:visible_chars]

            if visible_text:
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = font_size / 40
                thickness = 2
                (tw, th), baseline = cv2.getTextSize(visible_text, font, font_scale, thickness)

                if position[0] == "center":
                    x = (w - tw) // 2
                elif position[0] == "left":
                    x = 50
                else:
                    x = w - tw - 50

                if position[1] == "center":
                    y = (h + th) // 2
                elif position[1] == "top":
                    y = th + 50
                else:
                    y = h - 50

                cv2.putText(frame, visible_text, (x, y), font, font_scale, (255, 255, 255), thickness)

                if visible_chars < len(text) and int(t * 30) % 2 == 0:
                    cursor_x = x + tw + 5
                    cv2.rectangle(frame, (cursor_x, y - th), (cursor_x + 3, y), (255, 255, 255), -1)

            return frame

        return VideoClip(effect, duration=duration).set_fps(30)

    def fade_text(
        self,
        text: str,
        duration: float,
        resolution: Tuple[int, int],
        position: Tuple[str, str] = ("center", "center"),
        font_size: int = 60,
        fade_duration: float = 0.5,
    ) -> VideoClip:
        w, h = resolution

        def effect(get_frame, t):
            frame = np.zeros((h, w, 3), dtype=np.uint8)

            if t < fade_duration:
                alpha = t / fade_duration
            elif t > duration - fade_duration:
                alpha = (duration - t) / fade_duration
            else:
                alpha = 1.0

            alpha = max(0, min(1, alpha))

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = font_size / 40
            thickness = 2
            (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)

            if position[0] == "center":
                x = (w - tw) // 2
            elif position[0] == "left":
                x = 50
            else:
                x = w - tw - 50

            if position[1] == "center":
                y = (h + th) // 2
            elif position[1] == "top":
                y = th + 50
            else:
                y = h - 50

            color = int(255 * alpha)
            cv2.putText(frame, text, (x, y), font, font_scale, (color, color, color), thickness)

            return frame

        return VideoClip(effect, duration=duration).set_fps(30)

    def slide_text(
        self,
        text: str,
        duration: float,
        resolution: Tuple[int, int],
        direction: str = "left",
        font_size: int = 60,
        speed: float = 200,
    ) -> VideoClip:
        w, h = resolution

        def effect(get_frame, t):
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = font_size / 40
            thickness = 2
            (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)

            if direction == "left":
                x = w - int(t * speed)
            elif direction == "right":
                x = -tw + int(t * speed)
            elif direction == "up":
                x = (w - tw) // 2
            else:
                x = (w - tw) // 2

            if direction in ["up", "down"]:
                if direction == "up":
                    y = h - int(t * speed)
                else:
                    y = -th + int(t * speed)
                cv2.putText(frame, text, (x, y), font, font_scale, (255, 255, 255), thickness)
            else:
                y = (h + th) // 2
                if -tw < x < w:
                    cv2.putText(frame, text, (x, y), font, font_scale, (255, 255, 255), thickness)

            return frame

        return VideoClip(effect, duration=duration).set_fps(30)

    def glitch_text(
        self,
        text: str,
        duration: float,
        resolution: Tuple[int, int],
        font_size: int = 60,
        intensity: float = 1.0,
    ) -> VideoClip:
        import random
        w, h = resolution

        def effect(get_frame, t):
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = font_size / 40
            thickness = 2
            (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            x = (w - tw) // 2
            y = (h + th) // 2

            if random.random() < 0.3 * intensity:
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-5, 5)
                cv2.putText(frame, text, (x + offset_x, y + offset_y), font, font_scale, (0, 255, 0), thickness)
                cv2.putText(frame, text, (x - offset_x, y - offset_y), font, font_scale, (255, 0, 0), thickness)

            cv2.putText(frame, text, (x, y), font, font_scale, (255, 255, 255), thickness)

            return frame

        return VideoClip(effect, duration=duration).set_fps(30)

    def wave_text(
        self,
        text: str,
        duration: float,
        resolution: Tuple[int, int],
        font_size: int = 60,
        amplitude: int = 10,
        frequency: float = 3,
    ) -> VideoClip:
        w, h = resolution

        def effect(get_frame, t):
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = font_size / 40
            thickness = 2

            x_start = (w - len(text) * 20) // 2

            for i, char in enumerate(text):
                x = x_start + i * 20
                y_offset = int(amplitude * math.sin(2 * math.pi * frequency * t + i * 0.5))
                y = h // 2 + y_offset
                cv2.putText(frame, char, (x, y), font, font_scale, (255, 255, 255), thickness)

            return frame

        return VideoClip(effect, duration=duration).set_fps(30)

    def bounce_text(
        self,
        text: str,
        duration: float,
        resolution: Tuple[int, int],
        font_size: int = 60,
        bounce_height: int = 50,
    ) -> VideoClip:
        w, h = resolution

        def effect(get_frame, t):
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = font_size / 40
            thickness = 2
            (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            x = (w - tw) // 2

            bounce = abs(math.sin(t * 5)) * bounce_height
            y = (h + th) // 2 - int(bounce)

            shadow_offset = int(bounce / 10)
            cv2.putText(frame, text, (x + shadow_offset, y + shadow_offset), font, font_scale, (50, 50, 50), thickness)
            cv2.putText(frame, text, (x, y), font, font_scale, (255, 255, 255), thickness)

            return frame

        return VideoClip(effect, duration=duration).set_fps(30)

    def rotate_text(
        self,
        text: str,
        duration: float,
        resolution: Tuple[int, int],
        font_size: int = 60,
        rotation_speed: float = 2,
    ) -> VideoClip:
        w, h = resolution

        def effect(get_frame, t):
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = font_size / 40
            thickness = 2

            angle = t * rotation_speed * 360
            rad = math.radians(angle)

            center_x, center_y = w // 2, h // 2
            (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)

            cos_a = math.cos(rad)
            sin_a = math.sin(rad)

            points = [
                (-tw // 2, -th // 2),
                (tw // 2, -th // 2),
                (tw // 2, th // 2),
                (-tw // 2, th // 2),
            ]

            rotated = [
                (
                    int(center_x + px * cos_a - py * sin_a),
                    int(center_y + px * sin_a + py * cos_a),
                )
                for px, py in points
            ]

            cv2.fillPoly(frame, [np.array(rotated)], (255, 255, 255))

            return frame

        return VideoClip(effect, duration=duration).set_fps(30)
