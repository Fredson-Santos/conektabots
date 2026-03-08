#!/bin/sh

# Sai imediatamente se um comando falhar
set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "🧹 Limpando tabelas temporárias residuais do Alembic..."
    python -c "
import sqlite3, os
db = os.environ.get('DATABASE_URL', 'data/database.db')
if os.path.exists(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    # Remove tabelas temporarias residuais do batch_alter_table
    cur.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '_alembic_tmp_%'\")
    for (name,) in cur.fetchall():
        print(f'  Removendo tabela residual: {name}')
        cur.execute(f'DROP TABLE IF EXISTS \"{name}\"')
    # Se as tabelas ja existem mas alembic_version nao, marca como migrado
    cur.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='bot'\")
    has_tables = cur.fetchone() is not None
    cur.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'\")
    has_alembic = cur.fetchone() is not None
    if has_tables and not has_alembic:
        print('  Banco existente sem alembic_version. Marcando como migrado...')
        cur.execute('CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)')
        cur.execute(\"INSERT INTO alembic_version VALUES ('90de375b1de2')\")
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
