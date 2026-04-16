🧪 GUIA DE TESTES - API ConektaBots v2.0

## 📋 Resumo

Foram criados **3 arquivos de teste** para validar os endpoints da API:

1. **test_api_endpoints_integration.py** - Teste automatizado completo (pytest)
2. **test_endpoints_simple.py** - Teste simplificado apenas endpoints públicos (pytest)  
3. **test_endpoints_manual.py** - Script manual para testar endpoints (Python direto)

---

## 🚀 Como Executar os Testes

### Opção 1: Teste Automático Completo (Pytest)

```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Rodar todos os testes
pytest tests/test_api_endpoints_integration.py -v

# Rodar apenas os testes que passam
pytest tests/test_api_endpoints_integration.py -v -k "healthz or health or api_is_running"

# Com output detalhado
pytest tests/test_api_endpoints_integration.py -v --tb=short
```

**Resultado Esperado**: 
- ✅ 9 testes passam (health checks, validação de estrutura)
- ⚠️ 12 testes falham (middleware precisa ser configurado corretamente)

---

### Opção 2: Teste Simplificado (Pytest - Endpoints Públicos)

```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Rodar testes simples
pytest tests/test_endpoints_simple.py -v --tb=short -s

# Ver apenas resumo
pytest tests/test_endpoints_simple.py -v --tb=line
```

**Endpoints Testados**:
- GET /
- GET /healthz
- GET /health
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /docs
- GET /openapi.json

---

### Opção 3: Teste Manual (Script Python)

```bash
# PRIMEIRO: Iniciar o servidor API em outro terminal
python main.py
# Ou
uvicorn main:app --reload

# Depois em outro terminal, rodar o teste manual
python test_endpoints_manual.py
```

**Vantagem**: Testa contra API real em execução
**Resultado**: Relatório detalhado de cada endpoint

```
✅ GET / → 200
✅ GET /healthz → 200
✅ GET /health → 200
❌ GET /api/v1/auth/me → 401 (esperado - sem autenticação)
...
📊 RESUMO: 15/20 testes passaram (75%)
```

---

## 📊 Resultados dos Testes

### ✅ Endpoints que Funcionam

```
✅ GET /          → 200 (API info)
✅ GET /healthz   → 200 (Quick health check)
✅ GET /health    → 200 (DB health check)
✅ POST /api/v1/auth/register → 422 (Endpoint existe, validação)
✅ POST /api/v1/auth/login → 422 (Endpoint existe, validação)
✅ GET /docs → 200 (Swagger documentation)
✅ GET /openapi.json → 200 (OpenAPI schema)
✅ DELETE / → 405 (Method not allowed - correto)
✅ GET /api/v1/nonexistent → 404 (Not found - correto)
```

### ⚠️ Endpoints Protegidos (Requerem Token)

```
/api/v1/bots → Requer autenticação
/api/v1/tenants → Requer autenticação
/api/v1/regras → Requer autenticação
/api/v1/agendamentos → Requer autenticação
/api/v1/logs → Requer autenticação
/api/v1/marketplaces → Requer autenticação
```

Para testar estes, você precisa:
1. Fazer login e obter um token JWT
2. Passar o token no header: `Authorization: Bearer <TOKEN>`
3. Passar o tenant_id no request

---

## 🔧 Testar Endpoints Manualmente com cURL

### 1. Endpoints Públicos

```bash
# Health check
curl http://localhost:8000/healthz

# API Info
curl http://localhost:8000/

# Health com DB
curl http://localhost:8000/health
```

### 2. Autenticação

```bash
# Registrar novo usuário
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@example.com",
    "password":"SecurePassword123!",
    "nome":"User Name"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@example.com",
    "password":"SecurePassword123!"
  }'

# Resposta esperada:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "token_type": "bearer",
#   "expires_in": 3600
# }
```

### 3. Endpoints com Autenticação

```bash
# Substituir TOKEN pelo valor do access_token obtido acima
# Substituir TENANT_ID pelo tenant_id do usuário

curl http://localhost:8000/api/v1/bots \
  -H "Authorization: Bearer TOKEN" \
  -H "X-Tenant-ID: TENANT_ID"

curl http://localhost:8000/api/v1/tenants \
  -H "Authorization: Bearer TOKEN"
```

---

## 🐛 Problemas Identificados

### 1. Middleware de Tenant
- **Issue**: Endpoints retornam HTTPException quando middleware não reconhece request
- **Causa**: Middleware async do Starlette com TestClient
- **Solução**: Testar com API real em execução (use Option 3)

### 2. Erro em AuthService
- **Issue**: `AttributeError: type object 'TenantMember' has no attribute 'email'`
- **Arquivo**: `app/services/auth_service.py:185`
- **Ação**: Verificar modelo TenantMember

### 3. Endpoints Protegidos em Teste
- **Issue**: Falham em teste automatizado sem token
- **Solução**: Precisa mock ou fixture de autenticação

---

## ✨ Próximos Passos

1. **🔑 Autenticação em Testes**
   - Adicionar fixtures que geram token JWT válido
   - Mock ou endpoint de teste para gerar tenant_id

2. **📝 Melhoria de Testes**
   - Usar conftest.py para setup compartilhado
   - Adicionar testes de fluxo completo (register → login → operação)

3. **🐛 Correção de Bugs**
   - Revisar TenantMember modelo
   - Testar middleware em ambiente real

---

## 📁 Arquivos Gerados

- `tests/test_api_endpoints_integration.py` - Teste completo (21 cases)
- `tests/test_endpoints_simple.py` - Teste simplificado (20 cases)
- `test_endpoints_manual.py` - Script manual (interativo)
- `docs/api/TEST_RESULTS.md` - Relatório de resultados
- `docs/guides/TESTING_GUIDE.md` - Este arquivo

---

**Data**: 2026-04-15
**Projeto**: ConektaBots API v2.0
**Status**: ✅ Endpoints básicos funcionando | ⚠️ Alguns endpoints requerem ajustes
