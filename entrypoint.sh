#!/bin/sh

# Sai imediatamente se um comando falhar
set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "🧹 Limpando tabelas temporárias residuais do Alembic..."
    python -c "
import sqlite3, glob, os
db = os.environ.get('DATABASE_URL', 'data/database.db')
if os.path.exists(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '_alembic_tmp_%'\")
    for (name,) in cur.fetchall():
        print(f'  Removendo tabela residual: {name}')
        cur.execute(f'DROP TABLE IF EXISTS \"{name}\"')
    conn.commit()
    conn.close()
"

    echo "🚀 Iniciando migrações do banco de dados..."
    alembic upgrade head
    echo "✅ Migrações concluídas!"
else
    echo "⏭️ Migrações ignoradas (RUN_MIGRATIONS != true)"
fi

# Executa o comando passado para o container (CMD)
exec "$@"
