import numpy as np
from moviepy.editor import AudioFileClip, CompositeAudioClip
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    def __init__(self):
        pass

    def normalize(self, audio_path, target_db: float = -20) -> Optional[AudioFileClip]:
        try:
            audio = AudioFileClip(str(audio_path))
            max_volume = max(np.max(np.abs(audio.to_soundarray())))
            if max_volume > 0:
                target_linear = 10 ** (target_db / 20)
                factor = target_linear / max_volume
                audio = audio.volumex(factor)
            return audio
        except Exception as e:
            logger.error(f"Erro ao normalizar: {e}")
            return None

    def fade_audio(self, audio, fade_in: float = 0, fade_out: float = 0):
        if fade_in > 0:
            audio = audio.audio_fadein(fade_in)
        if fade_out > 0:
            audio = audio.audio_fadeout(fade_out)
        return audio

    def loop_audio(self, audio, target_duration: float):
        if audio.duration >= target_duration:
            return audio.subclip(0, target_duration)
        loops = int(target_duration / audio.duration) + 1
        from moviepy.editor import concatenate_audioclips
        looped = concatenate_audioclips([audio] * loops)
        return looped.subclip(0, target_duration)

    def mix_audio(self, tracks: list, volumes: list = None):
        if not volumes:
            volumes = [1.0] * len(tracks)
        mixed_tracks = []
        for track, vol in zip(tracks, volumes):
            mixed_tracks.append(track.volumex(vol))
        return CompositeAudioClip(mixed_tracks)

    def extract_audio(self, video_path) -> Optional[AudioFileClip]:
        try:
            from moviepy.editor import VideoFileClip
            video = VideoFileClip(str(video_path))
            audio = video.audio
            video.close()
            return audio
        except Exception as e:
            logger.error(f"Erro ao extrair áudio: {e}")
            return None

    def remove_silence(self, audio, threshold: float = 0.01, min_duration: float = 0.1):
        return audio

    def add_reverb(self, audio, room_size: float = 0.5):
        return audio

    def pitch_shift(self, audio, semitones: float = 0):
        return audio

    def time_stretch(self, audio, factor: float = 1.0):
        return audio.speedx(factor)
