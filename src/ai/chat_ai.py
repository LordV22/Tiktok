import json
import os
from mistralai import Mistral
from typing import Dict, Any, Optional
import logging

from .prompts import SYSTEM_PROMPT, SCENE_PROMPT, TEXT_PROMPT
from config import settings

logger = logging.getLogger(__name__)


class ChatAI:
    def __init__(self):
        self.client = Mistral(api_key=settings.mistral.api_key)
        self.model = settings.mistral.model
        self.history: Dict[int, list] = {}

    def chat(self, message: str, user_id: int) -> Dict[str, Any]:
        try:
            if user_id not in self.history:
                self.history[user_id] = []

            self.history[user_id].append({"role": "user", "content": message})

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(self.history[user_id][-10:])

            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=settings.mistral.temperature,
                max_tokens=settings.mistral.max_tokens,
            )

            content = response.choices[0].message.content.strip()
            content = self._clean_json(content)

            result = json.loads(content)

            self.history[user_id].append({"role": "assistant", "content": content})

            return {"success": True, "data": result}

        except json.JSONDecodeError:
            return self._fallback(message, user_id)
        except Exception as e:
            logger.error(f"Erro chat: {e}")
            return {"success": False, "error": str(e)}

    def generate_scenes(self, topic: str, style: str, duration: float) -> list:
        try:
            prompt = SCENE_PROMPT.format(topic=topic, style=style, duration=duration)
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            content = self._clean_json(response.choices[0].message.content)
            data = json.loads(content)
            return data.get("scenes", [])
        except Exception:
            return self._default_scenes(topic, duration)

    def generate_text(self, context: str, style: str = "modern") -> str:
        try:
            prompt = TEXT_PROMPT.format(context=context, style=style)
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=50,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return context[:30]

    def clear(self, user_id: int):
        self.history.pop(user_id, None)

    def _clean_json(self, content: str) -> str:
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()

    def _fallback(self, message: str, user_id: int) -> Dict[str, Any]:
        return {
            "success": True,
            "data": {
                "understanding": message,
                "video_type": "text2video",
                "duration": 15,
                "resolution": [1920, 1080],
                "style": "professional",
                "scenes": [
                    {
                        "start": 0,
                        "end": 15,
                        "bg_color": [20, 40, 80],
                        "text": message[:50],
                        "text_pos": "center",
                        "text_size": 60,
                        "text_color": "white",
                        "animation": "fade",
                        "effect": "vignette",
                    }
                ],
                "effects": ["fade_in", "fade_out"],
                "transitions": ["fade"],
                "audio": {"enabled": False},
                "suggestions": [],
            },
        }

    def _default_scenes(self, topic: str, duration: float) -> list:
        return [
            {
                "start": 0,
                "end": duration,
                "bg_color": [20, 40, 80],
                "text": topic[:50],
                "text_pos": "center",
                "text_size": 60,
                "text_color": "white",
                "animation": "fade",
                "effect": "none",
            }
        ]
