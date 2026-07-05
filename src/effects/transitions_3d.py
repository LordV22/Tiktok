import numpy as np
import cv2
from moviepy.editor import VideoClip
from typing import Tuple
import math


class Transitions3D:
    def __init__(self):
        pass

    def cube_rotate(
        self,
        clip_a: VideoClip,
        clip_b: VideoClip,
        duration: float = 1.0,
    ) -> VideoClip:
        w, h = clip_a.size

        def effect(get_frame, t):
            if t < duration:
                progress = t / duration
                angle = progress * 90

                frame_a = get_frame(t)

                M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, 1)
                scale_x = math.cos(math.radians(angle))
                M[0, 0] *= scale_x
                M[0, 2] += w * (1 - scale_x) / 2

                result = cv2.warpAffine(frame_a, M, (w, h))
                return result
            else:
                return get_frame(t - duration)

        return clip_a.fl(effect, duration=clip_a.duration + clip_b.duration)

    def flip_horizontal(
        self,
        clip_a: VideoClip,
        clip_b: VideoClip,
        duration: float = 1.0,
    ) -> VideoClip:
        w, h = clip_a.size

        def effect(get_frame, t):
            if t < duration:
                progress = t / duration
                frame_a = get_frame(t)

                scale_x = abs(math.cos(progress * math.pi))
                new_w = max(1, int(w * scale_x))

                if new_w > 0:
                    frame_resized = cv2.resize(frame_a, (new_w, h))
                    if scale_x > 0.5:
                        x_offset = (w - new_w) // 2
                        result = np.zeros((h, w, 3), dtype=np.uint8)
                        result[:, x_offset:x_offset + new_w] = frame_resized
                    else:
                        result = np.zeros((h, w, 3), dtype=np.uint8)
                else:
                    result = np.zeros((h, w, 3), dtype=np.uint8)

                return result
            else:
                return get_frame(t - duration)

        return clip_a.fl(effect, duration=clip_a.duration + clip_b.duration)

    def flip_vertical(
        self,
        clip_a: VideoClip,
        clip_b: VideoClip,
        duration: float = 1.0,
    ) -> VideoClip:
        w, h = clip_a.size

        def effect(get_frame, t):
            if t < duration:
                progress = t / duration
                frame_a = get_frame(t)

                scale_y = abs(math.cos(progress * math.pi))
                new_h = max(1, int(h * scale_y))

                if new_h > 0:
                    frame_resized = cv2.resize(frame_a, (w, new_h))
                    if scale_y > 0.5:
                        y_offset = (h - new_h) // 2
                        result = np.zeros((h, w, 3), dtype=np.uint8)
                        result[y_offset:y_offset + new_h, :] = frame_resized
                    else:
                        result = np.zeros((h, w, 3), dtype=np.uint8)
                else:
                    result = np.zeros((h, w, 3), dtype=np.uint8)

                return result
            else:
                return get_frame(t - duration)

        return clip_a.fl(effect, duration=clip_a.duration + clip_b.duration)

    def zoom_blur(
        self,
        clip_a: VideoClip,
        clip_b: VideoClip,
        duration: float = 1.0,
    ) -> VideoClip:
        w, h = clip_a.size

        def effect(get_frame, t):
            if t < duration:
                progress = t / duration
                frame_a = get_frame(t)

                if progress < 0.5:
                    scale = 1 + progress * 0.5
                    kernel_size = int(progress * 20)
                else:
                    scale = 1.25 - (progress - 0.5)
                    kernel_size = int((1 - progress) * 20)

                kernel_size = max(1, kernel_size if kernel_size % 2 == 1 else kernel_size + 1)
                blurred = cv2.GaussianBlur(frame_a, (kernel_size, kernel_size), 0)

                new_h, new_w = int(h * scale), int(w * scale)
                resized = cv2.resize(blurred, (new_w, new_h))

                x = (new_w - w) // 2
                y = (new_h - h) // 2
                result = resized[y:y + h, x:x + w]

                return result
            else:
                return get_frame(t - duration)

        return clip_a.fl(effect, duration=clip_a.duration + clip_b.duration)

    def spiral(
        self,
        clip_a: VideoClip,
        clip_b: VideoClip,
        duration: float = 1.0,
    ) -> VideoClip:
        w, h = clip_a.size

        def effect(get_frame, t):
            if t < duration:
                progress = t / duration
                frame_a = get_frame(t)

                angle = progress * 720
                scale = 1 - progress * 0.5

                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, scale)
                result = cv2.warpAffine(frame_a, M, (w, h))

                return result
            else:
                return get_frame(t - duration)

        return clip_a.fl(effect, duration=clip_a.duration + clip_b.duration)

    def pixelate_transition(
        self,
        clip_a: VideoClip,
        clip_b: VideoClip,
        duration: float = 1.0,
    ) -> VideoClip:
        w, h = clip_a.size

        def effect(get_frame, t):
            if t < duration:
                progress = t / duration
                frame_a = get_frame(t)

                if progress < 0.5:
                    pixel_size = max(1, int(50 * progress * 2))
                else:
                    pixel_size = max(1, int(50 * (1 - progress) * 2))

                small_w = max(1, w // pixel_size)
                small_h = max(1, h // pixel_size)
                small = cv2.resize(frame_a, (small_w, small_h))
                result = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

                return result
            else:
                return get_frame(t - duration)

        return clip_a.fl(effect, duration=clip_a.duration + clip_b.duration)

    def radial_wipe(
        self,
        clip_a: VideoClip,
        clip_b: VideoClip,
        duration: float = 1.0,
    ) -> VideoClip:
        w, h = clip_a.size

        def effect(get_frame, t):
            if t < duration:
                progress = t / duration
                frame_a = get_frame(t)

                center = (w // 2, h // 2)
                max_radius = math.sqrt(w**2 + h**2) / 2
                radius = max_radius * progress

                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.circle(mask, center, int(radius), 255, -1)

                result = frame_a.copy()
                result[mask == 0] = [0, 0, 0]

                return result
            else:
                return get_frame(t - duration)

        return clip_a.fl(effect, duration=clip_a.duration + clip_b.duration)

    def diamond_wipe(
        self,
        clip_a: VideoClip,
        clip_b: VideoClip,
        duration: float = 1.0,
    ) -> VideoClip:
        w, h = clip_a.size

        def effect(get_frame, t):
            if t < duration:
                progress = t / duration
                frame_a = get_frame(t)

                center_x, center_y = w // 2, h // 2
                size = int(max(w, h) * progress)

                mask = np.zeros((h, w), dtype=np.uint8)
                pts = np.array([
                    [center_x, center_y - size],
                    [center_x + size, center_y],
                    [center_x, center_y + size],
                    [center_x - size, center_y],
                ])
                cv2.fillPoly(mask, [pts], 255)

                result = frame_a.copy()
                result[mask == 0] = [0, 0, 0]

                return result
            else:
                return get_frame(t - duration)

        return clip_a.fl(effect, duration=clip_a.duration + clip_b.duration)

    def swirl(
        self,
        clip_a: VideoClip,
        clip_b: VideoClip,
        duration: float = 1.0,
    ) -> VideoClip:
        w, h = clip_a.size

        def effect(get_frame, t):
            if t < duration:
                progress = t / duration
                frame_a = get_frame(t)

                center = (w // 2, h // 2)
                strength = progress * 10

                Y, X = np.mgrid[:h, :w]
                X = X - center[0]
                Y = Y - center[1]

                R = np.sqrt(X**2 + Y**2)
                Theta = np.arctan2(Y, X) + strength * np.exp(-R / (max(w, h) / 4))

                X_new = (R * np.cos(Theta) + center[0]).astype(np.float32)
                Y_new = (R * np.sin(Theta) + center[1]).astype(np.float32)

                result = cv2.remap(frame_a, X_new, Y_new, cv2.INTER_LINEAR)
                return result
            else:
                return get_frame(t - duration)

        return clip_a.fl(effect, duration=clip_a.duration + clip_b.duration)
