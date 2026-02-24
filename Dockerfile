# 1. Wybieramy lekki obraz Linuxa z Pythonem 3.11
FROM python:3.11-slim

# 2. Ustawiamy katalog roboczy wewnątrz kontenera
WORKDIR /app

# 3. Instalujemy Poppler (wymagany przez pdf2image)
# Łączymy komendy && żeby warstwa była mniejsza
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# 4. Kopiujemy najpierw tylko listę bibliotek (dla cache'owania)
COPY requirements.txt .

# 5. Instalujemy biblioteki Pythonowe
RUN pip install --no-cache-dir -r requirements.txt

# 6. Kopiujemy resztę kodu aplikacji do kontenera
COPY . .

# 7. Uruchamiamy serwer
# UWAGA: "main:app" oznacza plik main.py i obiekt app = FastAPI()
# Host 0.0.0.0 jest konieczny, by kontener był widoczny w sieci Docker
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]