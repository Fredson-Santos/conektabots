#!/usr/bin/env python
"""
Gerenciador de Usuários Supabase
Comandos para criar, listar e gerenciar usuários
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Adicionar pasta app ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

import psycopg
from app.core.security import get_password_hash

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    """Conectar ao banco de dados Supabase"""
    try:
        conn = psycopg.connect(DATABASE_URL, autocommit=True)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        sys.exit(1)

def list_users():
    """Listar todos os usuários"""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    id,
                    email,
                    email_confirmed_at,
                    created_at,
                    updated_at,
                    last_sign_in_at,
                    role
                FROM auth.users
                ORDER BY created_at DESC
            """)
            
            users = cursor.fetchall()
            
            if not users:
                print("Nenhum usuário encontrado.")
                return
            
            print("\n" + "="*100)
            print(f"Total: {len(users)} usuários")
            print("="*100 + "\n")
            
            for user in users:
                uid, email, confirmed, created, updated, last_signin, role = user
                status = "✓ Confirmado" if confirmed else "⏳ Pendente"
                print(f"📧 Email: {email}")
                print(f"   ID: {uid}")
                print(f"   Status: {status}")
                print(f"   Criado: {created}")
                print(f"   Último login: {last_signin or 'Nunca'}")
                print()
        
        conn.close()
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

def create_user(email, password):
    """Criar novo usuário via Supabase API"""
    try:
        # Usar supabase-py se disponível, senão usar SQL direto
        import json
        import subprocess
        
        # Tentar via CLI (mais simples)
        result = subprocess.run(
            ["npx", "supabase", "branches", "auth", "create", "--email", email],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ Usuário {email} criado com sucesso!")
            print("  Verifique o email para confirmar a conta.")
        else:
            print(f"⚠ Resultado: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

def delete_user(user_id):
    """Deletar usuário"""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Verificar se existe
            cursor.execute("SELECT email FROM auth.users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                print(f"❌ Usuário {user_id} não encontrado")
                return
            
            # Deletar
            cursor.execute("DELETE FROM auth.users WHERE id = %s", (user_id,))
            print(f"✓ Usuário {user[0]} deletado")
        
        conn.close()
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Gerenciador de Usuários Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/supabase_users.py list
  python scripts/supabase_users.py create --email user@example.com --password senha123
  python scripts/supabase_users.py delete --user-id <UUID>
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a executar')
    
    # Comando: list
    subparsers.add_parser('list', help='Listar todos os usuários')
    
    # Comando: create
    create_parser = subparsers.add_parser('create', help='Criar novo usuário')
    create_parser.add_argument('--email', required=True, help='Email do usuário')
    create_parser.add_argument('--password', required=True, help='Senha do usuário')
    
    # Comando: delete
    delete_parser = subparsers.add_parser('delete', help='Deletar usuário')
    delete_parser.add_argument('--user-id', required=True, help='UUID do usuário')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'list':
        list_users()
    elif args.command == 'create':
        create_user(args.email, args.password)
    elif args.command == 'delete':
        delete_user(args.user_id)

if __name__ == '__main__':
    main()
