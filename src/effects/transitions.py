from moviepy.editor import VideoClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.compositing.transitions import crossfadein, crossfadeout
from moviepy.video.fx.all import fadein, fadeout
import numpy as np
from typing import Callable


class Transitions:
    def __init__(self):
        self.transitions = {
            "fade": self.fade,
            "crossfade": self.crossfade,
            "slide_left": self.slide_left,
            "slide_right": self.slide_right,
            "slide_up": self.slide_up,
            "slide_down": self.slide_down,
            "zoom": self.zoom_transition,
            "glitch": self.glitch_transition,
            "wipe": self.wipe,
            "dissolve": self.dissolve,
        }

    def get(self, name: str) -> Callable:
        return self.transitions.get(name, self.fade)

    def list(self) -> list:
        return list(self.transitions.keys())

    def apply(self, clip_a: VideoClip, clip_b: VideoClip, transition: str, duration: float = 1.0) -> VideoClip:
        func = self.get(transition)
        return func(clip_a, clip_b, duration)

    def fade(self, a: VideoClip, b: VideoClip, d: float = 1.0) -> VideoClip:
        a_faded = crossfadeout(a, d)
        b_faded = crossfadein(b, d)
        return concatenate_videoclips([a_faded, b_faded], method="compose")

    def crossfade(self, a: VideoClip, b: VideoClip, d: float = 1.0) -> VideoClip:
        a_faded = crossfadeout(a, d)
        b_faded = crossfadein(b, d)
        return concatenate_videoclips([a_faded, b_faded], method="compose")

    def slide_left(self, a: VideoClip, b: VideoClip, d: float = 1.0) -> VideoClip:
        def effect(get_frame, t):
            frame_a = get_frame(t)
            if t < d:
                progress = t / d
                w = frame_a.shape[1]
                offset = int(w * progress)
                return np.roll(frame_a, -offset, axis=1)
            return get_frame(t)
        return a.fl(effect)

    def slide_right(self, a: VideoClip, b: VideoClip, d: float = 1.0) -> VideoClip:
        def effect(get_frame, t):
            frame_a = get_frame(t)
            if t < d:
                progress = t / d
                w = frame_a.shape[1]
                offset = int(w * progress)
                return np.roll(frame_a, offset, axis=1)
            return get_frame(t)
        return a.fl(effect)

    def slide_up(self, a: VideoClip, b: VideoClip, d: float = 1.0) -> VideoClip:
        def effect(get_frame, t):
            frame_a = get_frame(t)
            if t < d:
                progress = t / d
                h = frame_a.shape[0]
                offset = int(h * progress)
                return np.roll(frame_a, -offset, axis=0)
            return get_frame(t)
        return a.fl(effect)

    def slide_down(self, a: VideoClip, b: VideoClip, d: float = 1.0) -> VideoClip:
        def effect(get_frame, t):
            frame_a = get_frame(t)
            if t < d:
                progress = t / d
                h = frame_a.shape[0]
                offset = int(h * progress)
                return np.roll(frame_a, offset, axis=0)
            return get_frame(t)
        return a.fl(effect)

    def zoom_transition(self, a: VideoClip, b: VideoClip, d: float = 1.0) -> VideoClip:
        def effect(get_frame, t):
            frame_a = get_frame(t)
            if t < d:
                progress = t / d
                scale = 1 + progress * 0.3
                h, w = frame_a.shape[:2]
                new_h, new_w = int(h * scale), int(w * scale)
                frame = __import__('cv2').resize(frame_a, (new_w, new_h))
                x = (new_w - w) // 2
                y = (new_h - h) // 2
                return frame[y:y+h, x:x+w]
            return get_frame(t)
        return a.fl(effect)

    def glitch_transition(self, a: VideoClip, b: VideoClip, d: float = 1.0) -> VideoClip:
        import random
        def effect(get_frame, t):
            frame = get_frame(t)
            if t < d:
                if random.random() < 0.3:
                    h, w = frame.shape[:2]
                    for _ in range(3):
                        y = random.randint(0, h)
                        sh = random.randint(5, 30)
                        off = random.randint(-20, 20)
                        ye = min(y + sh, h)
                        frame[y:ye] = np.roll(frame[y:ye], off, axis=1)
            return frame
        return a.fl(effect)

    def wipe(self, a: VideoClip, b: VideoClip, d: float = 1.0) -> VideoClip:
        def effect(get_frame, t):
            frame_a = get_frame(t)
            if t < d:
                progress = t / d
                h, w = frame_a.shape[:2]
                mask = np.zeros((h, w, 3), dtype=np.uint8)
                col = int(w * progress)
                mask[:, :col] = 255
                return (frame_a * (mask / 255)).astype(np.uint8)
            return frame_a
        return a.fl(effect)

    def dissolve(self, a: VideoClip, b: VideoClip, d: float = 1.0) -> VideoClip:
        def effect(get_frame, t):
            frame_a = get_frame(t)
            if t < d:
                progress = t / d
                alpha = 1 - progress
                return (frame_a * alpha).astype(np.uint8)
            return frame_a
        return a.fl(effect)
