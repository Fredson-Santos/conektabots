# Usa uma versão leve do Python
FROM python:3.10-slim

# Configurações para Python rodar melhor em container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Sao_Paulo

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para compilar algumas libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código (respeitando o .dockerignore)
COPY . .

# Expõe a porta que o FastAPI usa por padrão
EXPOSE 8000