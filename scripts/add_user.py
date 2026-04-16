#!/usr/bin/env python
"""
Script para adicionar usuários ao Supabase
Usar: python scripts/add_user.py --email user@example.com --password senha123
"""

import os
import sys
import argparse
import hashlib
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

import psycopg
from datetime import datetime, timezone

DATABASE_URL = os.getenv('DATABASE_URL')
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET', 'super-secret-jwt-token-with-at-least-32-characters-long')

def add_user(email: str, password: str, confirm: bool = True):
    """Adicionar usuário ao Supabase auth.users"""
    
    if not DATABASE_URL:
        print("❌ Erro: DATABASE_URL não configurada no .env")
        sys.exit(1)
    
    try:
        conn = psycopg.connect(DATABASE_URL, autocommit=True)
        cursor = conn.cursor()
        
        # Verificar se email já existe
        cursor.execute(
            "SELECT id FROM auth.users WHERE email = %s",
            (email,)
        )
        
        if cursor.fetchone():
            print(f"❌ Erro: Email {email} já existe")
            conn.close()
            return False
        
        # Gerar hash da senha (supabase usa bcrypt)
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(password)
        
        # Gerar UUID
        from uuid import uuid4
        user_id = str(uuid4())
        now = datetime.now(timezone.utc)
        
        # Inserir usuário
        cursor.execute("""
            INSERT INTO auth.users (
                id,
                email,
                encrypted_password,
                email_confirmed_at,
                created_at,
                updated_at,
                raw_user_meta_data,
                raw_app_meta_data,
                aud,
                confirmation_token
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            email,
            password_hash,
            now if confirm else None,  # email_confirmed_at
            now,
            now,
            '{}',  # raw_user_meta_data
            '{}',  # raw_app_meta_data
            'authenticated',
            '' if confirm else 'token_' + user_id[:16]
        ))
        
        print(f"✓ Usuário criado com sucesso!")
        print(f"  Email: {email}")
        print(f"  ID: {user_id}")
        print(f"  Status: {'Confirmado' if confirm else 'Pendente confirmação'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Adicionar usuário ao Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/add_user.py --email user@example.com --password senha123
  python scripts/add_user.py --email user@example.com --password senha123 --no-confirm
        """
    )
    
    parser.add_argument('--email', required=True, help='Email do usuário')
    parser.add_argument('--password', required=True, help='Senha do usuário')
    parser.add_argument('--no-confirm', action='store_true', help='Email não confirmado (requer verificação)')
    
    args = parser.parse_args()
    
    confirm = not args.no_confirm
    success = add_user(args.email, args.password, confirm)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
