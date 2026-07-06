import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env antes de qualquer import
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

from telegram.ext import ApplicationBuilder
from config import settings
from src.bots.telegram_bot import setup
from src.utils.logger import setup_logger, SecurityFilter

logger = setup_logger("videobot", settings.log_level, settings.paths.logs)


def main():
    logger.info("Iniciando VideoBot...")

    app = ApplicationBuilder().token(settings.telegram.token).build()

    security_filter = SecurityFilter()
    for handler in app.handlers:
        for h in handler.handlers if hasattr(handler, 'handlers') else [handler]:
            if hasattr(h, 'filters'):
                pass

    setup(app)

    logger.info("Bot pronto!")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
