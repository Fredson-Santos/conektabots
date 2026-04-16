# ConektaBots Backend 🐍

FastAPI + SQLAlchemy + PostgreSQL  
Multi-tenant SaaS backend com segurança enterprise.

## 📋 Rápido Start

```bash
# Instalar dependências
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configurar .env (copie de .env.example)
cp .env.example .env

# Executar migrações
alembic upgrade head

# Iniciar servidor
uvicorn main:app --reload --port 8000
```

**Server**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs  
**ReDoc**: http://localhost:8000/redoc

---

## 🗂️ Estrutura

```
backend/
├── app/
│   ├── core/              ← Configuração, database, segurança
│   │   ├── config.py      ← Pydantic settings
│   │   ├── database.py    ← SQLAlchemy engine + session
│   │   ├── deps.py        ← FastAPI dependencies (JWT, tenant, etc)
│   │   ├── security.py    ← Encryption + JWT validation
│   │   └── exceptions.py  ← Custom HTTP exceptions
│   │
│   ├── models/            ← SQLAlchemy ORM models (8 models)
│   │   ├── user.py
│   │   ├── tenant.py
│   │   ├── bot.py
│   │   ├── regra.py
│   │   ├── agendamento.py
│   │   └── ...
│   │
│   ├── schemas/           ← Pydantic DTOs para validação (126 schemas)
│   │   ├── auth.py
│   │   ├── bot.py
│   │   └── ...
│   │
│   ├── services/          ← Lógica de negócio (9 services)
│   │   ├── auth_service.py
│   │   ├── bot_service.py
│   │   ├── regex_service.py
│   │   ├── crypto_service.py
│   │   └── ...
│   │
│   ├── routers/           ← REST endpoints (8 routers, 40+ endpoints)
│   │   ├── auth.py
│   │   ├── bots.py
│   │   ├── tenants.py
│   │   └── ...
│   │
│   └── middleware/        ← Middleware (JWT, tenant, rate-limit)
│       ├── auth.py
│       ├── tenant.py
│       └── rate_limit.py
│
├── worker/                ← Background jobs (APScheduler)
│   ├── scheduler.py       ← Agendamentos
│   ├── message_processor.py ← Processa mensagens Telegram
│   ├── queue_manager.py   ← Fila com retry
│   └── marketplace_clients/ ← Integrações (Shopee, ML, etc)
│
├── tests/                 ← Testes pytest (23 casos)
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_crypto.py
│   └── ...
│
├── alembic/               ← Migrations (Alembic)
│   └── versions/
│
├── main.py                ← FastAPI app setup
├── requirements.txt       ← Dependencies
├── alembic.ini           ← Alembic config
└── .env.example          ← Environment template
```

---

## 🔐 Autenticação & Segurança

### JWT Flow
1. POST `/api/v1/auth/login` → Recebe `access_token` + `refresh_token`
2. Requests: `Authorization: Bearer {access_token}`
3. Token expira (30 min) → POST `/api/v1/auth/refresh` → novo token
4. POST `/api/v1/auth/logout` → revoga refresh token (opcional)

### Isolamento Multi-Tenant
- Cada user pertence a 1 tenant
- RLS (Row-Level Security) no banco: queries filtram por `tenant_id` automaticamente
- Backend: `Depends(get_current_tenant)` valida ownership

### Encriptação de Campos
- **Sensíveis**: `bot.api_hash`, `bot.session_string`, `marketplace.credenciais`
- **Método**: AES-256 (via `CryptoService`)
- **Chave**: Environment `DB_ENCRYPTION_KEY`

---

## 📊 Database

### Schema (PostgreSQL)
- **17 tabelas** (users, tenants, bots, regras, agendamentos, logs, etc)
- **Normalized**: Sem comma-separated fields (1:N relationships)
- **Soft Delete**: `deletado_em` timestamp (nunca hard delete)
- **Audit Trail**: `criado_em`, `atualizado_em` em tudo

### Migrations
```bash
# Ver status
alembic current
alembic history

# Criar nova migration
alembic revision --autogenerate -m "describe change"

# Aplicar upgrade
alembic upgrade head

# Fazer downgrade
alembic downgrade -1
```

---

## 🚀 Endpoints Principais

### Auth
```
POST   /api/v1/auth/signup          → Criar conta + tenant
POST   /api/v1/auth/login           → JWT tokens
POST   /api/v1/auth/refresh         → Novo access token
POST   /api/v1/auth/logout          → Revogar tokens
POST   /api/v1/auth/reset-password  → Reset
```

### Bots
```
GET    /api/v1/bots                 → Listar bots (tenant)
POST   /api/v1/bots                 → Criar bot
PATCH  /api/v1/bots/{id}            → Editar
DELETE /api/v1/bots/{id}            → Soft delete
POST   /api/v1/bots/{id}/toggle     → Ativar/desativar
```

### Regras
```
GET    /api/v1/regras               → Listar
POST   /api/v1/regras               → Criar
PATCH  /api/v1/regras/{id}          → Editar
DELETE /api/v1/regras/{id}          → Deletar
```

### Agendamentos
```
GET    /api/v1/agendamentos         → Listar
POST   /api/v1/agendamentos         → Criar
PATCH  /api/v1/agendamentos/{id}    → Editar
POST   /api/v1/agendamentos/{id}/enviar → Envio manual
```

### Marketplaces
```
GET    /api/v1/marketplaces         → Listar integrações
POST   /api/v1/marketplaces         → Criar
PATCH  /api/v1/marketplaces/{id}    → Editar credenciais
DELETE /api/v1/marketplaces/{id}    → Deletar
POST   /api/v1/marketplaces/{id}/test → Testar conexão
```

### Logs
```
GET    /api/v1/logs                 → Paginado com filtros
GET    /api/v1/stats                → Dashboard stats
```

---

## 🧪 Testes

```bash
# Rodar testes
pytest tests/

# Com cobertura
pytest tests/ --cov=app --cov-report=html

# Teste específico
pytest tests/test_auth.py -v

# Fixtures dinâmicas
pytest tests/ -k "test_login" -v
```

**Status Atual**: 23 testes, **9 passando** ✅

---

## 📦 Dependencies

See [requirements.txt](requirements.txt)

**Principais**:
- `fastapi` — Web framework
- `sqlalchemy` — ORM async
- `pydantic` — Validação
- `asyncpg` — PostgreSQL driver
- `python-jose` — JWT
- `passlib` — Password hashing
- `cryptography` — Encryption
- `pytest` — Testing

---

## 🔧 Environment Variables

See [.env.example](.env.example)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/conekta

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption
DB_ENCRYPTION_KEY=your-32-char-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Server
API_PORT=8000
```

---

## 🐳 Docker

```bash
# Build
docker build -t conektabots-backend .

# Run
docker run -it --env-file .env -p 8000:8000 conektabots-backend

# With docker-compose (from root)
cd ..
docker-compose up backend
```

---

## 🛟 Troubleshooting

**"CORS origin not allowed"**
- Adicione origem a `CORS_ORIGINS` em `.env`

**"JWT token expired"**
- Frontend deve chamar `/api/v1/auth/refresh`

**"Tenant not found"**
- User deve estar associado ao tenant (check RLS)

**"Database connection error"**
- Check `DATABASE_URL` environment variable
- Verifique credenciais PostgreSQL

---

## 📈 Roadmap

- ✅ Fase 2 Backend (100%)
  - Multi-tenant architecture
  - JWT authentication
  - Database schema (17 tables)
  - 40+ REST endpoints
  - Rate limiting
  - Encryption

- 🔜 Fase 3 Frontend (In Progress)
  - Next.js 15 dashboard
  - Auth pages
  - CRUD interfaces
  - Landing page

- 🔜 Fase 4 DevOps
  - CI/CD pipelines
  - Production deployment
  - Monitoring & logging

---

**Last Updated**: Abril 15, 2026

---

## 📞 Support

- 📖 Full API docs: http://localhost:8000/docs
- 🐛 Issues: GitHub issues
- 💬 Questions: Check .project/roadmap.md
