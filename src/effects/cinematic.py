import numpy as np
import cv2
from moviepy.editor import VideoClip
from typing import Callable, Dict, Any


class CinematicEffects:
    def __init__(self):
        self.effects = {
            "zoom_in": self.zoom_in,
            "zoom_out": self.zoom_out,
            "pan_left": self.pan_left,
            "pan_right": self.pan_right,
            "fade_in": self.fade_in,
            "fade_out": self.fade_out,
            "blur": self.blur,
            "glitch": self.glitch,
            "vhs": self.vhs,
            "chromatic": self.chromatic,
            "vignette": self.vignette,
            "shake": self.shake,
            "rgb_split": self.rgb_split,
            "scanlines": self.scanlines,
            "pixelate": self.pixelate,
            "light_leak": self.light_leak,
            "film_grain": self.film_grain,
            "thermal": self.thermal,
            "invert": self.invert,
            "emboss": self.emboss,
        }

    def get(self, name: str) -> Callable:
        return self.effects.get(name)

    def list(self) -> list:
        return list(self.effects.keys())

    def apply_chain(self, clip: VideoClip, effects: list) -> VideoClip:
        for e in effects:
            func = self.get(e)
            if func:
                clip = func(clip)
        return clip

    def zoom_in(self, clip: VideoClip, factor: float = 1.5, duration: float = 2.0):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            progress = min(t / duration, 1.0)
            scale = 1 + (factor - 1) * progress
            h, w = frame.shape[:2]
            new_h, new_w = int(h * scale), int(w * scale)
            frame = cv2.resize(frame, (new_w, new_h))
            x = (new_w - w) // 2
            y = (new_h - h) // 2
            return frame[y:y+h, x:x+w]
        return clip.fl(effect)

    def zoom_out(self, clip: VideoClip, factor: float = 1.5, duration: float = 2.0):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            progress = min(t / duration, 1.0)
            scale = factor - (factor - 1) * progress
            h, w = frame.shape[:2]
            new_h, new_w = int(h * scale), int(w * scale)
            frame = cv2.resize(frame, (new_w, new_h))
            x = (new_w - w) // 2
            y = (new_h - h) // 2
            return frame[y:y+h, x:x+w]
        return clip.fl(effect)

    def pan_left(self, clip: VideoClip, speed: float = 50):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            offset = int(speed * t) % frame.shape[1]
            return np.roll(frame, -offset, axis=1)
        return clip.fl(effect)

    def pan_right(self, clip: VideoClip, speed: float = 50):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            offset = int(speed * t) % frame.shape[1]
            return np.roll(frame, offset, axis=1)
        return clip.fl(effect)

    def fade_in(self, clip: VideoClip, duration: float = 1.0):
        return clip.crossfadein(duration)

    def fade_out(self, clip: VideoClip, duration: float = 1.0):
        return clip.crossfadeout(duration)

    def blur(self, clip: VideoClip, intensity: float = 1.0):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            k = int(31 * intensity)
            k = max(1, k if k % 2 == 1 else k + 1)
            return cv2.GaussianBlur(frame, (k, k), 0)
        return clip.fl(effect)

    def glitch(self, clip: VideoClip, intensity: float = 1.0):
        import random
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            if random.random() < 0.15 * intensity:
                h, w = frame.shape[:2]
                for _ in range(random.randint(3, 8)):
                    y = random.randint(0, h)
                    sh = random.randint(5, 50)
                    off = random.randint(-40, 40)
                    ye = min(y + sh, h)
                    frame[y:ye] = np.roll(frame[y:ye], off, axis=1)
            return frame
        return clip.fl(effect)

    def vhs(self, clip: VideoClip, intensity: float = 1.0):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            noise = np.random.normal(0, 10 * intensity, frame.shape).astype(np.uint8)
            frame = cv2.add(frame, noise)
            h = frame.shape[0]
            for y in range(0, h, 4):
                frame[y] = np.clip(frame[y].astype(np.int16) - int(8 * intensity), 0, 255).astype(np.uint8)
            return frame
        return clip.fl(effect)

    def chromatic(self, clip: VideoClip, offset: int = 6):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            result = frame.copy()
            result[:, :, 0] = np.roll(frame[:, :, 0], offset, axis=1)
            result[:, :, 2] = np.roll(frame[:, :, 2], -offset, axis=1)
            return result
        return clip.fl(effect)

    def vignette(self, clip: VideoClip, intensity: float = 0.5):
        def effect(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            Y, X = np.ogrid[:h, :w]
            cy, cx = h / 2, w / 2
            dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
            max_d = np.sqrt(cx**2 + cy**2)
            v = 1 - (dist / max_d) * intensity
            return (frame * np.clip(v, 0, 1)[:, :, np.newaxis]).astype(np.uint8)
        return clip.fl(effect)

    def shake(self, clip: VideoClip, amplitude: int = 10):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            h, w = frame.shape[:2]
            dx = int(amplitude * np.sin(t * 15))
            dy = int(amplitude * np.cos(t * 12))
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            return cv2.warpAffine(frame, M, (w, h))
        return clip.fl(effect)

    def rgb_split(self, clip: VideoClip, offset: int = 8):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            result = frame.copy()
            result[:, :, 0] = np.roll(frame[:, :, 0], offset, axis=1)
            result[:, :, 2] = np.roll(frame[:, :, 2], -offset, axis=1)
            return result
        return clip.fl(effect)

    def scanlines(self, clip: VideoClip, spacing: int = 4):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            frame = frame.copy()
            for y in range(0, frame.shape[0], spacing):
                frame[y] = np.clip(frame[y].astype(np.int16) - 15, 0, 255).astype(np.uint8)
            return frame
        return clip.fl(effect)

    def pixelate(self, clip: VideoClip, size: int = 10):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            h, w = frame.shape[:2]
            small = cv2.resize(frame, (w // size, h // size))
            return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        return clip.fl(effect)

    def light_leak(self, clip: VideoClip, color: tuple = (255, 200, 100)):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            frame = frame.astype(np.float32)
            h, w = frame.shape[:2]
            Y, X = np.ogrid[:h, :w]
            cy, cx = h * 0.7, w * 0.8
            dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
            max_d = np.sqrt(cx**2 + cy**2)
            leak = np.clip(1 - dist / max_d, 0, 1)
            frame[:, :, 0] = np.clip(frame[:, :, 0] + color[0] * leak * 0.4, 0, 255)
            frame[:, :, 1] = np.clip(frame[:, :, 1] + color[1] * leak * 0.4, 0, 255)
            frame[:, :, 2] = np.clip(frame[:, :, 2] + color[2] * leak * 0.4, 0, 255)
            return frame.astype(np.uint8)
        return clip.fl(effect)

    def film_grain(self, clip: VideoClip, intensity: float = 1.0):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            noise = np.random.normal(0, 15 * intensity, frame.shape).astype(np.uint8)
            return cv2.add(frame, noise)
        return clip.fl(effect)

    def thermal(self, clip: VideoClip):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            return cv2.addWeighted(frame, 0.5, thermal, 0.5, 0)
        return clip.fl(effect)

    def invert(self, clip: VideoClip):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            return 255 - frame
        return clip.fl(effect)

    def emboss(self, clip: VideoClip, intensity: float = 0.5):
        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
            embossed = cv2.filter2D(gray, -1, kernel)
            embossed = cv2.cvtColor(embossed, cv2.COLOR_GRAY2BGR)
            return cv2.addWeighted(frame, 1 - intensity, embossed, intensity, 0)
        return clip.fl(effect)
