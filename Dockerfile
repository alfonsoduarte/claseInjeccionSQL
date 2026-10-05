# Imagen fijada a la variante que ya esta descargada localmente.
# Si se cambia a python:3.12-slim, Docker intentara resolver otra etiqueta.
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Para probar la version corregida, cambiar a: ["python", "app_seguro.py"]
# y reconstruir con: docker compose up -d --build web
CMD ["python", "app.py"]
