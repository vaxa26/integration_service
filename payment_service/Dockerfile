# Basis-Image
FROM python:3.12-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Systemabhängigkeiten (optional, aber nützlich)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# FastAPI mit uvicorn starten
CMD ["uvicorn", "payment_service.app:app", "--host", "0.0.0.0", "--port", "8080"]
