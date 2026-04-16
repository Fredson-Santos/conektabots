#!/usr/bin/env python
"""Executar migrations Supabase via Python"""

import psycopg
from pathlib import Path

# Connection string do Supabase
conn_str = 'postgresql://postgres.uetuznqjnbppwwoaiyhe:6POswRcG1SCEcCNC@aws-1-sa-east-1.pooler.supabase.com:5432/postgres'

try:
    # Conectar
    with psycopg.connect(conn_str, autocommit=False) as conn:
        with conn.cursor() as cursor:
            print('✓ Conectado ao Supabase\n')
            
            # Listar migrations
            migrations_path = Path('supabase/migrations')
            migrations = sorted(migrations_path.glob('*.sql'))
            
            print(f'✓ Encontradas {len(migrations)} migrations:\n')
            for mig in migrations:
                print(f'  {mig.name}')
                
            # Executar cada migration
            print('\n' + '='*60)
            print('Executando migrations...')
            print('='*60 + '\n')
            
            for mig in migrations:
                sql_content = mig.read_text()
                try:
                    cursor.execute(sql_content)
                    conn.commit()
                    print(f'✓ {mig.name}')
                except Exception as e:
                    conn.rollback()
                    error_msg = str(e).split('\n')[0][:60]
                    print(f'✗ {mig.name}: {error_msg}')
            
            print('\n✓ Migrations concluídas!')
            
except Exception as e:
    print(f'✗ Erro de conexão: {e}')
