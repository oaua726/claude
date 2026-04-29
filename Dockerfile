FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev libpng-dev libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000

CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app
