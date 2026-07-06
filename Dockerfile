FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libgl1 \
    libglib2.0-0 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i 's/<policy domain="resource" name="memory" value="256MiB"\/>/<policy domain="resource" name="memory" value="512MiB"\/>/' /etc/ImageMagick-6/policy.xml 2>/dev/null || true
RUN sed -i 's/<policy domain="coder" rights="none" pattern="\*"/<policy domain="coder" rights="read|write" pattern="\*"/' /etc/ImageMagick-6/policy.xml 2>/dev/null || true

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p temp output logs

ENV PYTHONPATH=/app

CMD ["python", "main.py"]
