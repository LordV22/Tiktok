import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TelegramConfig:
    token: str = os.getenv("BOT_TOKEN", "")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    allowed_users: list = None

    def __post_init__(self):
        if self.allowed_users is None:
            users = os.getenv("ALLOWED_USERS", "")
            self.allowed_users = [int(u) for u in users.split(",") if u.strip()]


@dataclass
class MistralConfig:
    api_key: str = os.getenv("MISTRAL_API_KEY", "")
    model: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    temperature: float = 0.3
    max_tokens: int = 3000


@dataclass
class VideoConfig:
    max_duration: int = int(os.getenv("MAX_VIDEO_DURATION", "300"))
    fps: int = 30
    resolution: tuple = (1920, 1080)
    codec: str = "libx264"
    audio_codec: str = "aac"
    preset: str = "slow"
    crf: int = 18
    pixel_format: str = "yuv420p"


@dataclass
class PathConfig:
    base: Path = Path(__file__).parent.parent
    temp: Path = None
    output: Path = None
    logs: Path = None

    def __post_init__(self):
        self.temp = Path(os.getenv("TEMP_DIR", "./temp"))
        self.output = Path(os.getenv("OUTPUT_DIR", "./output"))
        self.logs = Path(os.getenv("LOG_DIR", "./logs"))
        for p in [self.temp, self.output, self.logs]:
            p.mkdir(parents=True, exist_ok=True)


@dataclass
class Settings:
    telegram: TelegramConfig = None
    mistral: MistralConfig = None
    video: VideoConfig = None
    paths: PathConfig = None
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def __post_init__(self):
        self.telegram = TelegramConfig()
        self.mistral = MistralConfig()
        self.video = VideoConfig()
        self.paths = PathConfig()


settings = Settings()
