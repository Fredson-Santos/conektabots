# ConektaBots - Monorepo Structure 🏗️

**Date**: Abril 15, 2026  
**Phase**: Fase 3 Frontend + Reorganização  
**Architecture**: Monorepo (Backend + Frontend separados)

---

## 📁 Nova Estrutura

```
conektabots/
├── backend/                      ← FastAPI + SQLAlchemy (mover)
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── middleware/
│   ├── worker/                   ← Background jobs
│   ├── tests/
│   ├── alembic/                  ← Database migrations
│   ├── supabase/
│   ├── main.py
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── .env.example
│   ├── .gitignore
│   └── README.md
│
├── frontend/                     ← Next.js 15 (criar)
│   ├── app/
│   │   ├── (auth)/
│   │   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── .env.local.example
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── .gitignore
│   └── README.md
│
├── .github/
│   ├── workflows/               ← CI/CD
│   │   ├── test-backend.yml
│   │   ├── lint-backend.yml
│   │   ├── deploy-backend.yml
│   │   └── deploy-frontend.yml
│   ├── instructions/
│   └── skills/
│
├── .project/
│   ├── phase3-tasks.md          ✅ Criado
│   ├── roadmap.md
│   ├── state.md
│   ├── changelog.md
│   ├── conventions.md
│   └── implementation-log.md
│
├── docs/
├── .gitignore                   ← ATUALIZAR (adicionar /backend/node_modules, etc)
├── docker-compose.yml           ← ATUALIZAR (referências)
└── README.md                    ← ATUALIZAR (instruções de setup)

```

---

## 🔄 Passos de Reorganização

### Passo 1: Mover código backend para /backend
```bash
# 1. Criar diretório /backend
mkdir backend

# 2. Mover arquivos Python (NÃO deletar, apenas mover)
# Estes vão: app/, worker/, tests/, alembic/, requirements.txt, main.py, etc
mv app/ backend/
mv worker/ backend/
mv tests/ backend/
mv alembic/ backend/
mv alembic.ini backend/
mv main.py backend/
mv requirements.txt backend/
mv run_migrations.py backend/

# 3. Arquivos que FICAM na raiz
# .github/, .project/, docs/, docker-compose.yml, README.md, etc
```

### Passo 2: Criar /frontend com Next.js
```bash
# 1. Criar projeto Next.js
cd conektabots
npx create-next-app@latest frontend --typescript --tailwind --eslint --app

# 2. Estrutura pronta para começar
```

### Passo 3: Atualizar configurações
- `.gitignore` — adicionar `/backend/node_modules`, `/frontend/node_modules`, `/frontend/.next`
- `docker-compose.yml` — atualizar paths para `./backend/`
- `.github/workflows/` — atualizar paths
- `README.md` — instruções de setup separadas para `/backend` e `/frontend`

---

## 📝 Environment Variables

### Backend (.env)
```
# database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/conekta_dev

# jwt
JWT_SECRET=your-secret-key-change-in-prod
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# encryption
DB_ENCRYPTION_KEY=your-encryption-key-change-in-prod

# cors
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# server
API_PORT=8000
WEB_PORT=3000
```

### Frontend (.env.local)
```
# API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_PATH=/api/v1

# App
NEXT_PUBLIC_APP_NAME=ConektaBots
NEXT_PUBLIC_APP_VERSION=1.0.0
```

---

## 🚀 Setup Local (Novo Workflow)

```bash
# 1. Backend setup
cd conektabots/backend
python -m venv venv
source venv/Scripts/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 2. Frontend setup (em outro terminal)
cd conektabots/frontend
npm install
npm run dev  # Inicia em http://localhost:3000
```

---

## 📦 Docker Compose (Atualizado)

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/conekta_dev
      - CORS_ORIGINS=http://localhost:3000,http://frontend:3000
    depends_on:
      - postgres

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: conekta_dev
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

---

## 🔄 Timeline

| Etapa | Task | Tempo | Status |
|-------|------|-------|--------|
| **Reorganização** | Move backend → /backend | 30min | ⏳ Proximo |
| **A1** | Setup Next.js em /frontend | 8-10h | 🔄 In Progress |
| **A2** | Backend validation (CORS) | 3-4h | ⏳ Depois |
| **B1** | Auth pages | 6-8h | ⏳ Depois |
| **C1+** | Dashboard + CRUD | 40-50h | ⏳ Depois |

---

## ✅ Checklist antes de começar

- [ ] Backend code moved to `/backend/`
- [ ] `/frontend/` criado com Next.js
- [ ] `.gitignore` atualizado
- [ ] `docker-compose.yml` atualizado
- [ ] `README.md` atualizado com instruções separadas
- [ ] Backend roda em `http://localhost:8000`
- [ ] Frontend roda em `http://localhost:3000`
- [ ] CORS configurado para localhost:3000

---

**Próximo Step**: Executar reorganização e depois começar Task A1!
