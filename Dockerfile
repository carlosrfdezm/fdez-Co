# Imagen base ligera de Python
FROM python:3.11-slim

# Instalar dependencias básicas de compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la aplicación
WORKDIR /app

# Copiar requirements primero para aprovechar cache
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Variables de entorno básicas
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=sandbox.settings

# Comando de inicio con Gunicorn
CMD ["gunicorn", "sandbox.wsgi:application", "--bind", "0.0.0.0:$PORT"]
