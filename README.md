# 🎬 VideoBot Pro

Bot de Telegram com IA para geração de vídeos profissionais.

## 🧠 Arquitetura

```
🧠 Mistral AI     → Lógica e Inteligência
📷 OpenCV         → Visão e Efeitos
✂️ MoviePy        → Montagem e Sincronia
⚙️ FFmpeg         → Renderização Potente
🛡️ Telegram Bot   → Entrega Segura
```

## 🚀 Funcionalidades

### 💬 Chat com IA
Descreva o vídeo em linguagem natural e a IA cria automaticamente.

### 📸 Criar com Imagens
Envie fotos e crie slideshow profissionais.

### 🎬 Criar do Zero
Gere vídeos apenas com descrição de texto.

### ✨ 30+ Efeitos Profissionais

#### Efeitos Básicos
- Zoom In/Out
- Pan Left/Right
- Fade In/Out
- Blur

#### Efeitos Cinematográficos
- Glitch
- VHS
- Chromatic Aberration
- Vignette
- Film Grain
- Light Leak
- Lens Flare

#### Efeitos de Partículas
- Snow (Neve)
- Rain (Chuva)
- Fire (Fogo)
- Sparkles (Brilhos)
- Smoke (Fumaça)
- Bubbles (Bolhas)
- Confetti (Confete)

#### Texto Animado
- Typewriter
- Fade Text
- Slide Text
- Glitch Text
- Wave Text
- Bounce Text
- Rotate Text

#### Transições 3D
- Cube Rotate
- Flip Horizontal/Vertical
- Zoom Blur
- Spiral
- Pixelate
- Radial/Diamond Wipe
- Swirl

#### Overlays
- Lens Flare
- Light Leaks
- Bokeh
- Scan Lines
- Film Grain
- RGB Shift
- Heat Wave
- Mirror
- Kaleidoscope

#### Color Grading
- Cinematic
- Warm/Cool
- Vintage
- Noir
- Cyberpunk
- Sunset/Ocean/Forest/Rose

### 🎨 Templates Premium
- Business
- Social Reels
- YouTube Intro
- Presentation
- Gaming
- Wedding
- Food
- Fitness
- Travel
- Minimalist

### 🛡️ Segurança
- Marca d'água
- Validação de arquivos
- Limpeza automática
- Log seguro

## 📋 Pré-requisitos

- Python 3.10+
- FFmpeg
- API Key da Mistral AI
- Bot Token do Telegram

## ⚙️ Instalação

```bash
# Clone
git clone <repo>
cd video-bot

# Ambiente virtual
python -m venv venv
source venv/bin/activate

# Dependências
pip install -r requirements.txt

# Configure
cp .env .env.example
# Edite .env

# Execute
python main.py
```

## 🐳 Docker

```bash
docker-compose up -d
```

## 📁 Estrutura

```
video-bot/
├── main.py
├── .env
├── .gitignore
├── config/
│   ├── settings.py
│   └── security.py
├── src/
│   ├── ai/
│   │   ├── chat_ai.py
│   │   └── prompts.py
│   ├── bots/
│   │   └── telegram_bot.py
│   ├── core/
│   │   ├── pipeline.py
│   │   ├── render.py
│   │   └── validator.py
│   ├── effects/
│   │   ├── cinematic.py
│   │   ├── particles.py
│   │   ├── text_animations.py
│   │   ├── transitions.py
│   │   ├── transitions_3d.py
│   │   ├── overlays.py
│   │   ├── color_grading.py
│   │   └── security.py
│   ├── templates/
│   │   └── library.py
│   ├── audio/
│   │   └── processor.py
│   └── utils/
│       ├── files.py
│       └── logger.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 📝 Licença

MIT License
