import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
from .crypto import crypto_manager

load_dotenv()


class SecureConfig:
    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get(self, key: str, default: str = "", decrypt: bool = False) -> str:
        cache_key = f"{key}_{decrypt}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        value = os.getenv(key, default)

        if value.startswith("ENC:"):
            try:
                decrypted = crypto_manager.decrypt(value[4:], context=key)
                self._cache[cache_key] = decrypted
                return decrypted
            except Exception:
                self._cache[cache_key] = value
                return value

        self._cache[cache_key] = value
        return value

    def get_int(self, key: str, default: int = 0) -> int:
        return int(self.get(key, str(default)))

    def get_bool(self, key: str, default: bool = False) -> bool:
        return self.get(key, str(default)).lower() == "true"

    def get_list(self, key: str, default: list = None) -> list:
        val = self.get(key, "")
        if not val:
            return default or []
        return [x.strip() for x in val.split(",") if x.strip()]

    def encrypt_value(self, value: str, key: str = None) -> str:
        encrypted = crypto_manager.encrypt(value, context=key or "config")
        return f"ENC:{encrypted}"


secure = SecureConfig()


@dataclass
class TelegramConfig:
    token: str = secure.get("BOT_TOKEN")
    max_file_size_mb: int = secure.get_int("MAX_FILE_SIZE_MB", 50)
    allowed_users: list = None

    def __post_init__(self):
        if self.allowed_users is None:
            self.allowed_users = secure.get_list("ALLOWED_USERS")


@dataclass
class MistralConfig:
    api_key: str = secure.get("MISTRAL_API_KEY")
    model: str = secure.get("MISTRAL_MODEL", "mistral-small-latest")
    temperature: float = float(secure.get("MISTRAL_TEMPERATURE", "0.3"))
    max_tokens: int = secure.get_int("MISTRAL_MAX_TOKENS", 3000)


@dataclass
class VideoConfig:
    max_duration: int = secure.get_int("MAX_VIDEO_DURATION", 300)
    fps: int = secure.get_int("VIDEO_FPS", 30)
    resolution: tuple = (1920, 1080)
    codec: str = secure.get("VIDEO_CODEC", "libx264")
    audio_codec: str = secure.get("AUDIO_CODEC", "aac")
    preset: str = secure.get("VIDEO_PRESET", "slow")
    crf: int = secure.get_int("VIDEO_CRF", 18)
    pixel_format: str = "yuv420p"


@dataclass
class SecurityConfig:
    master_key: str = secure.get("MASTER_KEY", "")
    admin_id: int = secure.get_int("ADMIN_ID", 0)
    encryption_enabled: bool = secure.get_bool("ENCRYPTION_ENABLED", True)
    kdf_salt: str = secure.get("KDF_SALT", "")
    token_expiry: int = secure.get_int("TOKEN_EXPIRY", 3600)


@dataclass
class PathConfig:
    base: Path = Path(__file__).parent.parent
    temp: Path = None
    output: Path = None
    logs: Path = None
    encrypted: Path = None

    def __post_init__(self):
        self.temp = Path(secure.get("TEMP_DIR", "./temp"))
        self.output = Path(secure.get("OUTPUT_DIR", "./output"))
        self.logs = Path(secure.get("LOG_DIR", "./logs"))
        self.encrypted = Path("./encrypted")
        for p in [self.temp, self.output, self.logs, self.encrypted]:
            p.mkdir(parents=True, exist_ok=True)


@dataclass
class Settings:
    telegram: TelegramConfig = None
    mistral: MistralConfig = None
    video: VideoConfig = None
    security: SecurityConfig = None
    paths: PathConfig = None
    debug: bool = secure.get_bool("DEBUG")
    log_level: str = secure.get("LOG_LEVEL", "INFO")

    def __post_init__(self):
        self.telegram = TelegramConfig()
        self.mistral = MistralConfig()
        self.video = VideoConfig()
        self.security = SecurityConfig()
        self.paths = PathConfig()

    def encrypt_env_value(self, key: str, value: str) -> str:
        return secure.encrypt_value(value, key)

    def get_crypto_info(self) -> dict:
        return {
            "encryption": "AES-256-GCM",
            "key_derivation": "Argon2id",
            "integrity": "HMAC-SHA512",
            "key_exchange": "RSA-4096",
            "tokenization": True,
            "audit_log": True,
            "vault": True,
        }


settings = Settings()
