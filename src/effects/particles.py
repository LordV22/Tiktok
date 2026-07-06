import numpy as np
import cv2
from moviepy.editor import VideoClip, CompositeVideoClip, ColorClip
from typing import List, Tuple, Optional
import random
import math


class Particle:
    def __init__(self, x, y, vx, vy, life, color, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        return self.life > 0

    def get_alpha(self):
        return max(0, self.life / self.max_life)


class ParticleSystem:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.particles: List[Particle] = []

    def emit(
        self,
        count: int,
        x: float,
        y: float,
        spread: float = 100,
        color: Tuple[int, int, int] = (255, 255, 255),
        size_range: Tuple[int, int] = (2, 8),
        life_range: Tuple[float, float] = (0.5, 2.0),
        velocity_range: Tuple[float, float] = (-50, 50),
    ):
        for _ in range(count):
            px = x + random.uniform(-spread, spread)
            py = y + random.uniform(-spread, spread)
            vx = random.uniform(*velocity_range)
            vy = random.uniform(*velocity_range)
            life = random.uniform(*life_range)
            size = random.randint(*size_range)
            self.particles.append(Particle(px, py, vx, vy, life, color, size))

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]

    def render(self, frame: np.ndarray) -> np.ndarray:
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        overlay = np.require(frame.copy(), dtype=np.uint8, requirements=['C_CONTIGUOUS'])
        for p in self.particles:
            alpha = p.get_alpha()
            color = tuple(int(c * alpha) for c in p.color)
            cv2.circle(overlay, (int(p.x), int(p.y)), p.size, color, -1)
        return cv2.addWeighted(frame, 1, overlay, 0.8, 0)

    def clear(self):
        self.particles.clear()


class ParticleEffects:
    def __init__(self):
        pass

    def snow(self, clip: VideoClip, count: int = 100, speed: float = 100) -> VideoClip:
        w, h = clip.size

        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            ps = ParticleSystem(w, h)

            if random.random() < 0.3:
                ps.emit(
                    count=5,
                    x=w / 2,
                    y=0,
                    spread=w / 2,
                    color=(255, 255, 255),
                    size_range=(2, 6),
                    life_range=(2, 4),
                    velocity_range=(-20, 20),
                )

            for _ in range(count):
                x = random.randint(0, w)
                y = int((t * speed + random.randint(0, h)) % h)
                ps.emit(count=1, x=x, y=y, spread=0, size_range=(2, 4), life_range=(0.1, 0.2))

            ps.update(0.03)
            return ps.render(frame)

        return clip.fl(effect)

    def rain(self, clip: VideoClip, count: int = 200, speed: float = 300) -> VideoClip:
        w, h = clip.size

        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            overlay = np.require(frame.copy(), dtype=np.uint8, requirements=["C_CONTIGUOUS"])

            for _ in range(count):
                x = random.randint(0, w)
                y = int((t * speed + random.randint(0, h)) % h)
                length = random.randint(10, 30)
                cv2.line(overlay, (x, y), (x - 2, y + length), (200, 200, 255), 1)

            return cv2.addWeighted(frame, 1, overlay, 0.5, 0)

        return clip.fl(effect)

    def fire(self, clip: VideoClip, x: float = None, y: float = None) -> VideoClip:
        w, h = clip.size
        cx = x or w // 2
        cy = y or h * 0.8

        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            overlay = np.require(frame.copy(), dtype=np.uint8, requirements=["C_CONTIGUOUS"])

            for _ in range(20):
                fx = cx + random.uniform(-30, 30)
                fy = cy - random.uniform(0, 80)
                size = random.randint(5, 15)
                alpha = random.uniform(0.3, 0.8)
                color = (
                    int(50 * alpha),
                    int(100 * alpha),
                    int(255 * alpha),
                )
                cv2.circle(overlay, (int(fx), int(fy)), size, color, -1)

            return cv2.addWeighted(frame, 1, overlay, 0.6, 0)

        return clip.fl(effect)

    def sparkles(self, clip: VideoClip, count: int = 50) -> VideoClip:
        w, h = clip.size

        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            overlay = np.require(frame.copy(), dtype=np.uint8, requirements=["C_CONTIGUOUS"])

            for _ in range(count):
                x = random.randint(0, w)
                y = random.randint(0, h)
                size = random.randint(1, 4)
                brightness = random.randint(150, 255)
                color = (brightness, brightness, brightness)
                cv2.circle(overlay, (x, y), size, color, -1)

                if random.random() < 0.3:
                    length = random.randint(5, 15)
                    cv2.line(overlay, (x - length, y), (x + length, y), color, 1)
                    cv2.line(overlay, (x, y - length), (x, y + length), color, 1)

            return cv2.addWeighted(frame, 1, overlay, 0.7, 0)

        return clip.fl(effect)

    def smoke(self, clip: VideoClip, x: float = None, y: float = None) -> VideoClip:
        w, h = clip.size
        cx = x or w // 2
        cy = y or h

        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            overlay = np.require(frame.copy(), dtype=np.uint8, requirements=["C_CONTIGUOUS"])

            for _ in range(15):
                sx = cx + random.uniform(-50, 50)
                sy = cy - random.uniform(0, 150)
                size = random.randint(20, 60)
                alpha = random.uniform(0.1, 0.3)
                gray = int(100 * alpha)
                color = (gray, gray, gray)
                cv2.circle(overlay, (int(sx), int(sy)), size, color, -1)

            return cv2.addWeighted(frame, 1, overlay, 0.4, 0)

        return clip.fl(effect)

    def bubbles(self, clip: VideoClip, count: int = 30) -> VideoClip:
        w, h = clip.size

        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            overlay = np.require(frame.copy(), dtype=np.uint8, requirements=["C_CONTIGUOUS"])

            for i in range(count):
                x = int((i * 73 + t * 30) % w)
                y = int(h - ((i * 47 + t * 50) % h))
                size = random.randint(5, 20)
                cv2.circle(overlay, (x, y), size, (255, 255, 255), 2)
                cv2.circle(overlay, (x - 3, y - 3), 3, (255, 255, 255), -1)

            return cv2.addWeighted(frame, 1, overlay, 0.5, 0)

        return clip.fl(effect)

    def confetti(self, clip: VideoClip, count: int = 100) -> VideoClip:
        w, h = clip.size
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
        ]

        def effect(get_frame, t):
            frame = get_frame(t)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            overlay = np.require(frame.copy(), dtype=np.uint8, requirements=["C_CONTIGUOUS"])

            for _ in range(count):
                x = random.randint(0, w)
                y = int((t * 100 + random.randint(0, h)) % h)
                color = random.choice(colors)
                size = random.randint(3, 8)
                angle = random.randint(0, 360)
                pts = self._rotate_rect(x, y, size, angle)
                cv2.fillPoly(overlay, [pts], color)

            return cv2.addWeighted(frame, 1, overlay, 0.6, 0)

        return clip.fl(effect)

    def _rotate_rect(self, x, y, size, angle):
        pts = np.array([
            [-size, -size],
            [size, -size],
            [size, size],
            [-size, size],
        ], dtype=np.float32)
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        rotated = np.array([
            [px * cos_a - py * sin_a, px * sin_a + py * cos_a]
            for px, py in pts
        ])
        rotated[:, 0] += x
        rotated[:, 1] += y
        return rotated.astype(np.int32)
