FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libgl1 \
    libglib2.0-0 \
    fonts-dejavu-core \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/ImageMagick-7 /etc/ImageMagick-6

RUN POLICY='<policymap>\
  <policy domain="resource" name="memory" value="512MiB"/>\
  <policy domain="resource" name="map" value="512MiB"/>\
  <policy domain="resource" name="width" value="16KP"/>\
  <policy domain="resource" name="height" value="16KP"/>\
  <policy domain="resource" name="area" value="128MP"/>\
  <policy domain="resource" name="disk" value="1GiB"/>\
  <policy domain="module" rights="none" pattern="{PS1,PS2,PS3,EPS,PDF,XPS}" />\
</policymap>' && \
    echo "$POLICY" > /etc/ImageMagick-7/policy.xml 2>/dev/null; \
    echo "$POLICY" > /etc/ImageMagick-6/policy.xml 2>/dev/null; \
    true

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p temp output logs

ENV PYTHONPATH=/app

CMD ["python", "main.py"]
