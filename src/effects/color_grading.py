import numpy as np
from moviepy.editor import VideoClip
import cv2


class ColorGrading:
    def __init__(self):
        self.luts = {
            "cinematic": self._cinematic_lut,
            "warm": self._warm_lut,
            "cool": self._cool_lut,
            "vintage": self._vintage_lut,
            "noir": self._noir_lut,
            "cyberpunk": self._cyberpunk_lut,
            "sunset": self._sunset_lut,
            "ocean": self._ocean_lut,
            "forest": self._forest_lut,
            "rose": self._rose_lut,
        }

    def apply(self, clip: VideoClip, lut_name: str, intensity: float = 1.0) -> VideoClip:
        lut_func = self.luts.get(lut_name, self._cinematic_lut)

        def effect(get_frame, t):
            frame = get_frame(t)
            graded = lut_func(frame)
            return cv2.addWeighted(frame, 1 - intensity, graded, intensity, 0)

        return clip.fl(effect)

    def _cinematic_lut(self, frame: np.ndarray) -> np.ndarray:
        result = frame.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * 0.8 + 20, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 0.9, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.1, 0, 255)
        return result.astype(np.uint8)

    def _warm_lut(self, frame: np.ndarray) -> np.ndarray:
        result = frame.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * 1.1, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 0.9, 0, 255)
        return result.astype(np.uint8)

    def _cool_lut(self, frame: np.ndarray) -> np.ndarray:
        result = frame.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * 0.9, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.2, 0, 255)
        return result.astype(np.uint8)

    def _vintage_lut(self, frame: np.ndarray) -> np.ndarray:
        result = frame.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * 0.9 + 30, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 0.8 + 20, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 0.7 + 10, 0, 255)
        return result.astype(np.uint8)

    def _noir_lut(self, frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        result = result.astype(np.float32)
        result = np.clip(result * 1.2, 0, 255)
        return result.astype(np.uint8)

    def _cyberpunk_lut(self, frame: np.ndarray) -> np.ndarray:
        result = frame.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * 1.3 + 30, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 0.7, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.4 + 20, 0, 255)
        return result.astype(np.uint8)

    def _sunset_lut(self, frame: np.ndarray) -> np.ndarray:
        result = frame.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * 1.2 + 40, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 0.9 + 10, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 0.8, 0, 255)
        return result.astype(np.uint8)

    def _ocean_lut(self, frame: np.ndarray) -> np.ndarray:
        result = frame.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * 0.7, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 1.1 + 20, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.3 + 30, 0, 255)
        return result.astype(np.uint8)

    def _forest_lut(self, frame: np.ndarray) -> np.ndarray:
        result = frame.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * 0.8, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 1.2 + 20, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 0.7, 0, 255)
        return result.astype(np.uint8)

    def _rose_lut(self, frame: np.ndarray) -> np.ndarray:
        result = frame.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * 1.1 + 30, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * 0.8, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.1 + 20, 0, 255)
        return result.astype(np.uint8)


class AdvancedColorGrading:
    def __init__(self):
        self.grader = ColorGrading()

    def match_look(
        self,
        clip: VideoClip,
        target: str = "cinematic",
        exposure: float = 0,
        contrast: float = 0,
        saturation: float = 0,
        temperature: float = 0,
        tint: float = 0,
        shadows: float = 0,
        highlights: float = 0,
    ) -> VideoClip:
        def effect(get_frame, t):
            frame = get_frame(t).astype(np.float32)

            if exposure != 0:
                frame = frame * (1 + exposure)

            if contrast != 0:
                factor = 1 + contrast
                frame = (frame - 128) * factor + 128

            if saturation != 0:
                gray = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_BGR2GRAY)
                gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR).astype(np.float32)
                frame = frame + (frame - gray) * saturation

            if temperature > 0:
                frame[:, :, 0] += temperature * 20
                frame[:, :, 2] -= temperature * 10
            elif temperature < 0:
                frame[:, :, 0] += temperature * 10
                frame[:, :, 2] -= temperature * 20

            if tint != 0:
                frame[:, :, 1] += tint * 15

            if shadows != 0:
                mask = (frame < 80).astype(np.float32)
                frame += mask * shadows * 50

            if highlights != 0:
                mask = (frame > 175).astype(np.float32)
                frame += mask * highlights * 50

            return np.clip(frame, 0, 255).astype(np.uint8)

        return clip.fl(effect)

    def apply_lut(self, clip: VideoClip, lut_name: str, intensity: float = 1.0) -> VideoClip:
        return self.grader.apply(clip, lut_name, intensity)

    def list_luts(self) -> list:
        return list(self.grader.luts.keys())
