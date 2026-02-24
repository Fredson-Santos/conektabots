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

# Dá permissão de execução ao script de entrada
RUN chmod +x entrypoint.sh

# Expõe a porta que o FastAPI usa por padrão
EXPOSE 8000

# Script que roda antes de iniciar o app (para migrações)
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando oficial para o painel web (pode ser sobrescrito pelo compose)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]