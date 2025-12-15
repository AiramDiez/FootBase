# -----------------------------------------------------------
# 🐍 Imagen base optimizada
# -----------------------------------------------------------
FROM python:3.11-bullseye

# -----------------------------------------------------------
# ⚙️ Configuración general
# -----------------------------------------------------------
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependencias necesarias para cryptography, neo4j y llama-index
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------
# 📦 Instalación de dependencias Python
# -----------------------------------------------------------
COPY requirements.txt .

# Mejoras de pip para evitar timeouts del resolver
RUN pip install --upgrade pip setuptools wheel \
    && pip config set global.timeout 1200 \
    && pip config set global.retries 5 \
    && pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------
# 🧩 Copia del código fuente
# -----------------------------------------------------------
COPY app ./app

# -----------------------------------------------------------
# 🧠 Variables de entorno por defecto (sobreescribibles)
# -----------------------------------------------------------
ENV NEO4J_URI=bolt://sibi-neo4j:7687
ENV NEO4J_USER=neo4j
ENV NEO4J_PASS=recovery123
ENV API_KEY=seleccionador123

# -----------------------------------------------------------
# 🚀 Comando de ejecución
# -----------------------------------------------------------
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
