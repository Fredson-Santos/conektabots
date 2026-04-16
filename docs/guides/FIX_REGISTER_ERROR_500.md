🔧 CORREÇÃO DO ERRO 500 NO REGISTRO

═══════════════════════════════════════════════════════════════════════════════

## PROBLEMA IDENTIFICADO

O erro 500 ao fazer registro era causado por uma mismatch entre o design do 
banco de dados e a implementação do AuthService:

```
app/services/auth_service.py:115
  member = TenantMember(
      email=req.email,              ❌ ERRO: TenantMember não tem 'email'
      senha_hash=self.hash_password(...),  ❌ ERRO: não tem 'senha_hash'
      role="owner",
      ativo=True,                   ❌ ERRO: não tem 'ativo'
  )
```

O modelo TenantMember foi criado com:
- `id` (UUID)
- `tenant_id` (FK)
- `user_id` (UUID referência do usuário)
- `role` (String)
- `criado_em`, `atualizado_em`, `deletado_em` (timestamps)

Mas NÃO tinha campos para email, senha, ou ativo.

═══════════════════════════════════════════════════════════════════════════════

## SOLUÇÃO IMPLEMENTADA

### 1. Criado novo modelo: app/models/user.py

Nova tabela `user` para armazenar credenciais locais:
- `id` (UUID PK)
- `email` (String, unique, indexed para login)
- `senha_hash` (String, hash bcrypt)
- `nome` (String)
- `ativo` (Boolean)
- `criado_em`, `atualizado_em`, `deletado_em` (timestamps)

### 2. Relacionamentos Atualizados

**User** (1) ← → (*) **TenantMember**
- User pode estar em múltiplos tenants
- TenantMember.user_id é FK para User.id

**Tenant** (1) ← → (*) **TenantMember**  
- Um tenant pode ter múltiplos membros
- TenantMember.tenant_id é FK para Tenant.id

### 3. Corrigido AuthService

#### Método `register()`:
- Cria User (com email, senha_hash, nome)
- Cria Tenant
- Cria TenantMember (ligando User → Tenant com role="owner")
- Retorna tokens JWT

#### Método `login()`:
- Busca User por email
- Verifica senha
- Busca TenantMember do usuário
- Retorna tokens JWT com tenant_id

#### Método `refresh_token()`:
- Busca User por user_id do token
- Busca TenantMember
- Retorna novo token de acesso

### 4. Corrigido app/core/deps.py

- `get_current_user()`: Converte string user_id para UUID
- `get_current_tenant()`: Filtra por user_id e deletado_em == None
- `require_role()`: Adiciona validação de soft-delete

### 5. Atualizado models/__init__.py

- Adicionado import de User
- Adicionado User ao __all__

═══════════════════════════════════════════════════════════════════════════════

## FLUXO DE REGISTRO CORRIGIDO

```
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "nome": "User Name"
}
```

### Passos internos:

1. ✅ Validar que email não existe em User
2. ✅ Hash de senha com bcrypt
3. ✅ Criar registro User
4. ✅ Flush para obter User.id
5. ✅ Criar Tenant (slug, plano="free")
6. ✅ Flush para obter Tenant.id
7. ✅ Criar TenantMember(user_id=User.id, tenant_id=Tenant.id, role="owner")
8. ✅ Commit transaction
9. ✅ Gerar JWT tokens
10. ✅ Retornar TokenResponse

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "owner"
}
```

═══════════════════════════════════════════════════════════════════════════════

## MIGRAÇÕES CRIADAS

### 1. Alembic (Banco Local - SQLite/PostgreSQL)
Arquivo: `alembic/versions/001_add_user_table.py`

Para aplicar:
```bash
alembic upgrade head
```

### 2. Supabase (Banco em Nuvem)
Arquivo: `supabase/migrations/008_add_user_table.sql`

Para aplicar no Supabase:
1. Dashboard → SQL Editor
2. Copiar conteúdo do arquivo
3. Executar SQL
4. Ou usar: `supabase migration up`

═══════════════════════════════════════════════════════════════════════════════

## TESTES RECOMENDADOS

### 1. Testar Registro
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePassword123!",
    "nome": "New User"
  }'
```

Esperado: 201 Created com tokens

### 2. Testar Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePassword123!"
  }'
```

Esperado: 200 OK com tokens

### 3. Testar com Token
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

Esperado: 200 OK com dados do usuário

═══════════════════════════════════════════════════════════════════════════════

## CHECKLIST DE VALIDAÇÃO

- ✅ Modelo User criado
- ✅ Relacionamento User ↔ TenantMember configurado
- ✅ AuthService.register() corrigido
- ✅ AuthService.login() corrigido
- ✅ AuthService.refresh_token() corrigido
- ✅ app/core/deps.py atualizado
- ✅ models/__init__.py atualizado
- ✅ Migração Alembic criada
- ✅ Migração Supabase criada
- ⏳ Rodar migrações (alembic upgrade head + supabase migration up)
- ⏳ Testar registro
- ⏳ Testar login

═══════════════════════════════════════════════════════════════════════════════

## PRÓXIMAS AÇÕES

1. Aplicar migração Alembic ou Supabase
2. Reiniciar servidor FastAPI
3. Testar endpoints de autenticação
4. Se aparecer erro em produção, check logs para erro específico
5. Executar script de testes de endpoints

═══════════════════════════════════════════════════════════════════════════════

Data: 2026-04-15
Status: PRONTO PARA TESTAR ✅
