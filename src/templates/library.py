from dataclasses import dataclass
from typing import Dict, Any, List
import json
from pathlib import Path


@dataclass
class Template:
    name: str
    description: str
    resolution: tuple
    fps: int
    duration: float
    style: str
    color_palette: List[tuple]
    fonts: List[str]
    effects: List[str]
    transitions: List[str]
    text_animation: str
    layout: Dict[str, Any]


class TemplateLibrary:
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self._load_defaults()

    def _load_defaults(self):
        self.templates = {
            "business": Template(
                name="business",
                description="Corporate e profissional",
                resolution=(1920, 1080),
                fps=30,
                duration=30,
                style="professional",
                color_palette=[(20, 40, 80), (255, 255, 255), (0, 120, 200)],
                fonts=["Arial", "Helvetica", "Roboto"],
                effects=["fade_in", "fade_out", "vignette"],
                transitions=["fade", "slide_left"],
                text_animation="fade",
                layout={"title_size": 72, "subtitle_size": 36, "position": "center"},
            ),
            "social_reels": Template(
                name="social_reels",
                description="Para Instagram Reels e TikTok",
                resolution=(1080, 1920),
                fps=30,
                duration=15,
                style="modern",
                color_palette=[(30, 30, 40), (255, 255, 255), (255, 0, 100)],
                fonts=["Impact", "Arial Black", "Bebas Neue"],
                effects=["glitch", "zoom_in", "shake"],
                transitions=["glitch", "slide_up"],
                text_animation="typewriter",
                layout={"title_size": 80, "subtitle_size": 40, "position": "center"},
            ),
            "youtube_intro": Template(
                name="youtube_intro",
                description="Intro para YouTube",
                resolution=(1920, 1080),
                fps=30,
                duration=10,
                style="creative",
                color_palette=[(40, 20, 60), (255, 200, 0), (255, 255, 255)],
                fonts=["Montserrat", "Poppins", "Raleway"],
                effects=["zoom_in", "light_leak", "chromatic"],
                transitions=["zoom_blur", "fade"],
                text_animation="bounce",
                layout={"title_size": 96, "subtitle_size": 48, "position": "center"},
            ),
            "presentation": Template(
                name="presentation",
                description="Apresentação profissional",
                resolution=(1920, 1080),
                fps=30,
                duration=60,
                style="minimal",
                color_palette=[(240, 240, 240), (50, 50, 50), (0, 150, 136)],
                fonts=["Garamond", "Georgia", "Times New Roman"],
                effects=["fade_in", "fade_out"],
                transitions=["fade", "dissolve"],
                text_animation="fade",
                layout={"title_size": 64, "subtitle_size": 32, "position": "left"},
            ),
            "gaming": Template(
                name="gaming",
                description="Para conteúdo gaming",
                resolution=(1920, 1080),
                fps=60,
                duration=20,
                style="gaming",
                color_palette=[(10, 10, 20), (0, 255, 255), (255, 0, 255)],
                fonts=["Orbitron", "Rajdhani", "Press Start 2P"],
                effects=["glitch", "rgb_split", "scanlines", "vhs"],
                transitions=["glitch", "pixelate"],
                text_animation="glitch",
                layout={"title_size": 80, "subtitle_size": 40, "position": "center"},
            ),
            "wedding": Template(
                name="wedding",
                description="Cerimônia e casamento",
                resolution=(1920, 1080),
                fps=30,
                duration=60,
                style="elegant",
                color_palette=[(255, 248, 240), (212, 175, 55), (180, 140, 100)],
                fonts=["Great Vibes", "Playfair Display", "Cormorant Garamond"],
                effects=["fade_in", "fade_out", "vignette", "bokeh"],
                transitions=["fade", "dissolve"],
                text_animation="fade",
                layout={"title_size": 72, "subtitle_size": 36, "position": "center"},
            ),
            "food": Template(
                name="food",
                description="Restaurante e gastronomia",
                resolution=(1080, 1080),
                fps=30,
                duration=15,
                style="warm",
                color_palette=[(60, 30, 20), (255, 200, 100), (255, 255, 255)],
                fonts=["Playfair Display", "Lora", "Merriweather"],
                effects=["zoom_in", "light_leak", "warm"],
                transitions=["fade", "slide_left"],
                text_animation="typewriter",
                layout={"title_size": 64, "subtitle_size": 32, "position": "center"},
            ),
            "fitness": Template(
                name="fitness",
                description="Academia e fitness",
                resolution=(1080, 1920),
                fps=30,
                duration=20,
                style="energetic",
                color_palette=[(20, 20, 20), (255, 50, 50), (255, 255, 255)],
                fonts=["Oswald", "Bebas Neue", "Anton"],
                effects=["shake", "zoom_in", "glitch"],
                transitions=["slide_up", "zoom_blur"],
                text_animation="bounce",
                layout={"title_size": 80, "subtitle_size": 40, "position": "center"},
            ),
            "travel": Template(
                name="travel",
                description="Viagens e turismo",
                resolution=(1920, 1080),
                fps=30,
                duration=30,
                style="cinematic",
                color_palette=[(20, 40, 60), (255, 200, 100), (100, 180, 255)],
                fonts=["Raleway", "Montserrat", "Lato"],
                effects=["vignette", "light_leak", "film_grain"],
                transitions=["fade", "dissolve", "radial_wipe"],
                text_animation="slide",
                layout={"title_size": 72, "subtitle_size": 36, "position": "center"},
            ),
            "minimalist": Template(
                name="minimalist",
                description="Limpo e minimalista",
                resolution=(1920, 1080),
                fps=30,
                duration=20,
                style="minimal",
                color_palette=[(255, 255, 255), (30, 30, 30), (200, 200, 200)],
                fonts=["Helvetica Neue", "Futura", "Avenir"],
                effects=["fade_in", "fade_out"],
                transitions=["fade"],
                text_animation="fade",
                layout={"title_size": 60, "subtitle_size": 30, "position": "center"},
            ),
        }

    def get(self, name: str) -> Template:
        return self.templates.get(name)

    def list(self) -> list:
        return [
            {"name": t.name, "description": t.description}
            for t in self.templates.values()
        ]

    def create(self, template: Template):
        self.templates[template.name] = template

    def save(self, path: Path):
        data = {}
        for name, t in self.templates.items():
            data[name] = {
                "name": t.name,
                "description": t.description,
                "resolution": list(t.resolution),
                "fps": t.fps,
                "duration": t.duration,
                "style": t.style,
                "color_palette": [list(c) for c in t.color_palette],
                "fonts": t.fonts,
                "effects": t.effects,
                "transitions": t.transitions,
                "text_animation": t.text_animation,
                "layout": t.layout,
            }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, path: Path):
        with open(path) as f:
            data = json.load(f)
        for name, t_data in data.items():
            self.templates[name] = Template(
                name=t_data["name"],
                description=t_data["description"],
                resolution=tuple(t_data["resolution"]),
                fps=t_data["fps"],
                duration=t_data["duration"],
                style=t_data["style"],
                color_palette=[tuple(c) for c in t_data["color_palette"]],
                fonts=t_data["fonts"],
                effects=t_data["effects"],
                transitions=t_data["transitions"],
                text_animation=t_data["text_animation"],
                layout=t_data["layout"],
            )
