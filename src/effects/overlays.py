import numpy as np
from moviepy.editor import VideoClip
from typing import Tuple


class OverlayEffects:
    def __init__(self):
        pass

    def lens_flare(
        self,
        clip: VideoClip,
        position: Tuple[int, int] = None,
        color: Tuple[int, int, int] = (255, 255, 200),
        intensity: float = 0.5,
    ) -> VideoClip:
        w, h = clip.size
        pos = position or (w * 0.7, h * 0.3)

        def effect(get_frame, t):
            frame = get_frame(t).astype(np.float32)
            Y, X = np.ogrid[:h, :w]
            dist = np.sqrt((X - pos[0]) ** 2 + (Y - pos[1]) ** 2)
            flare = np.exp(-dist / 150) * intensity
            frame[:, :, 0] = np.clip(frame[:, :, 0] + color[0] * flare, 0, 255)
            frame[:, :, 1] = np.clip(frame[:, :, 1] + color[1] * flare, 0, 255)
            frame[:, :, 2] = np.clip(frame[:, :, 2] + color[2] * flare, 0, 255)
            return frame.astype(np.uint8)

        return clip.fl(effect)

    def light_leaks(
        self,
        clip: VideoClip,
        colors: list = None,
        intensity: float = 0.4,
    ) -> VideoClip:
        w, h = clip.size
        colors = colors or [
            (255, 100, 50),
            (255, 200, 100),
            (255, 150, 80),
        ]

        def effect(get_frame, t):
            frame = get_frame(t).astype(np.float32)
            color = colors[int(t) % len(colors)]

            Y, X = np.ogrid[:h, :w]
            center_x = w * (0.3 + 0.4 * np.sin(t * 0.5))
            center_y = h * (0.3 + 0.4 * np.cos(t * 0.3))

            dist = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
            leak = np.exp(-dist / (max(w, h) / 3)) * intensity

            frame[:, :, 0] = np.clip(frame[:, :, 0] + color[0] * leak, 0, 255)
            frame[:, :, 1] = np.clip(frame[:, :, 1] + color[1] * leak, 0, 255)
            frame[:, :, 2] = np.clip(frame[:, :, 2] + color[2] * leak, 0, 255)

            return frame.astype(np.uint8)

        return clip.fl(effect)

    def bokeh(
        self,
        clip: VideoClip,
        count: int = 20,
        color: Tuple[int, int, int] = (255, 255, 255),
        max_size: int = 50,
    ) -> VideoClip:
        w, h = clip.size
        np.random.seed(42)
        positions = [(np.random.randint(0, w), np.random.randint(0, h)) for _ in range(count)]
        sizes = [np.random.randint(10, max_size) for _ in range(count)]
        opacities = [np.random.uniform(0.1, 0.4) for _ in range(count)]

        def effect(get_frame, t):
            frame = get_frame(t).copy()

            for (x, y), size, opacity in zip(positions, sizes, opacities):
                y_pos = int((y + t * 20) % h)
                overlay = frame.copy()
                cv2.circle(overlay, (x, y_pos), size, color, -1)
                frame = cv2.addWeighted(frame, 1, overlay, opacity, 0)

            return frame

        return clip.fl(effect)

    def scan_lines(
        self,
        clip: VideoClip,
        spacing: int = 4,
        opacity: float = 0.3,
    ) -> VideoClip:
        w, h = clip.size

        def effect(get_frame, t):
            frame = get_frame(t).copy()
            for y in range(0, h, spacing):
                frame[y, :] = np.clip(
                    frame[y, :].astype(np.int16) - int(50 * opacity), 0, 255
                ).astype(np.uint8)
            return frame

        return clip.fl(effect)

    def film_grain(
        self,
        clip: VideoClip,
        intensity: float = 0.1,
    ) -> VideoClip:
        def effect(get_frame, t):
            frame = get_frame(t)
            noise = np.random.normal(0, 255 * intensity, frame.shape).astype(np.int16)
            result = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            return result

        return clip.fl(effect)

    def vignette_animated(
        self,
        clip: VideoClip,
        intensity: float = 0.5,
        speed: float = 0.5,
    ) -> VideoClip:
        w, h = clip.size

        def effect(get_frame, t):
            frame = get_frame(t)
            Y, X = np.ogrid[:h, :w]
            cx, cy = w / 2, h / 2
            dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
            max_dist = np.sqrt(cx**2 + cy**2)

            dynamic_intensity = intensity * (0.8 + 0.2 * np.sin(t * speed))
            vignette = 1 - (dist / max_dist) * dynamic_intensity
            vignette = np.clip(vignette, 0, 1)[:, :, np.newaxis]

            return (frame * vignette).astype(np.uint8)

        return clip.fl(effect)

    def chromatic_aberration_animated(
        self,
        clip: VideoClip,
        max_offset: int = 10,
        speed: float = 2,
    ) -> VideoClip:
        def effect(get_frame, t):
            frame = get_frame(t)
            offset = int(max_offset * np.sin(t * speed))
            result = frame.copy()
            result[:, :, 0] = np.roll(frame[:, :, 0], offset, axis=1)
            result[:, :, 2] = np.roll(frame[:, :, 2], -offset, axis=1)
            return result

        return clip.fl(effect)

    def rgb_shift(
        self,
        clip: VideoClip,
        offset: int = 5,
    ) -> VideoClip:
        def effect(get_frame, t):
            frame = get_frame(t)
            result = frame.copy()
            result[:, :, 0] = np.roll(frame[:, :, 0], offset, axis=1)
            result[:, :, 1] = np.roll(frame[:, :, 1], -offset // 2, axis=0)
            result[:, :, 2] = np.roll(frame[:, :, 2], -offset, axis=1)
            return result

        return clip.fl(effect)

    def heat_wave(
        self,
        clip: VideoClip,
        amplitude: int = 5,
        frequency: float = 3,
    ) -> VideoClip:
        w, h = clip.size

        def effect(get_frame, t):
            frame = get_frame(t)
            result = np.zeros_like(frame)

            for y in range(h):
                offset = int(amplitude * np.sin(y / 20 + t * frequency))
                result[y, :] = np.roll(frame[y, :], offset, axis=0)

            return result

        return clip.fl(effect)

    def mirror_effect(
        self,
        clip: VideoClip,
        axis: int = 1,
        offset: int = 0,
    ) -> VideoClip:
        def effect(get_frame, t):
            frame = get_frame(t)
            if axis == 1:
                half = frame.shape[1] // 2
                left = frame[:, :half]
                right = np.flip(frame[:, half:], axis=1)
                return np.concatenate([left, right], axis=1)
            else:
                half = frame.shape[0] // 2
                top = frame[:half, :]
                bottom = np.flip(frame[half:, :], axis=0)
                return np.concatenate([top, bottom], axis=0)

        return clip.fl(effect)

    def kaleidoscope(
        self,
        clip: VideoClip,
        segments: int = 6,
    ) -> VideoClip:
        w, h = clip.size

        def effect(get_frame, t):
            frame = get_frame(t)
            center_x, center_y = w // 2, h // 2
            result = frame.copy()

            for i in range(1, segments):
                angle = (360 / segments) * i
                M = cv2.getRotationMatrix2D((center_x, center_y), angle, 1)
                rotated = cv2.warpAffine(frame, M, (w, h))

                mask = np.zeros((h, w), dtype=np.uint8)
                pts = np.array([
                    [center_x, center_y],
                    [int(center_x + w * np.cos(np.radians(angle - 360 / segments / 2))),
                     int(center_y + h * np.sin(np.radians(angle - 360 / segments / 2)))],
                    [int(center_x + w * np.cos(np.radians(angle))),
                     int(center_y + h * np.sin(np.radians(angle)))],
                ])
                cv2.fillPoly(mask, [pts], 255)

                result[mask > 0] = rotated[mask > 0]

            return result

        return clip.fl(effect)


import cv2
