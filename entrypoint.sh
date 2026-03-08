#!/bin/sh

# Sai imediatamente se um comando falhar
set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "🚀 Iniciando migrações do banco de dados..."
    alembic upgrade head
    echo "✅ Migrações concluídas!"
else
    echo "⏭️ Migrações ignoradas (RUN_MIGRATIONS != true)"
fi

# Executa o comando passado para o container (CMD)
exec "$@"
