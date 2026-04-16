# Fase 3 - Frontend Implementation Tasks 🚀

**Phase**: Fase 3 - Frontend (Next.js 15)  
**Created**: Abril 15, 2026  
**Target Completion**: 3-4 weeks  
**Deployment**: Vercel  
**Database**: PostgreSQL (local) + FastAPI JWT  
**Status**: 📍 In Progress

---

## 📊 Task Overview

| Task | Subtask | Status | Assignee | Est. Hours | Dependencies |
|------|---------|--------|----------|-----------|-------------|
| **A0** | Reorganizar para monorepo (/backend + /frontend) | ⏳ PENDING | Backend Dev | 1-2h | ✅ Estrutura pronta |
| **A1** | Setup Next.js 15 + Auth Infrastructure | ⏳ PENDING | Frontend Designer | 8-10h | → A0 ✅ |
| **A2** | Backend Validation (CORS + Endpoints) | ⏳ PENDING | Backend Dev | 3-4h | → A1 |
| **B1** | Auth Pages (Login/Signup/Protected Routes) | ⏳ PENDING | Frontend Designer | 6-8h | → A1 ✅ |
| **C1** | Dashboard Layout Base | ⏳ PENDING | Frontend Designer | 4-6h | → B1 |
| **D1** | Bots Management CRUD | ⏳ PENDING | Frontend Designer | 6-8h | → C1 |
| **D2** | Rules Management CRUD (Complex Form) | ⏳ PENDING | Frontend Designer | 10-12h | → C1 |
| **D3** | Schedules Management CRUD (Complex Form) | ⏳ PENDING | Frontend Designer | 10-12h | → C1 |
| **D4** | Marketplaces CRUD (Dynamic Forms) ⭐ | ⏳ PENDING | Frontend + Backend | 8-10h | → C1 |
| **D5** | Logs Viewer (Table + Filters + Export) | ⏳ PENDING | Frontend Designer | 6-8h | → C1 |
| **D6** | Settings & Account Management | ⏳ PENDING | Frontend Designer | 6-8h | → C1 |
| **E1** | Marketing Landing Page | ⏳ PENDING | Frontend Designer | 6-8h | // Paralelo com D |
| **F1** | Polish & UX (Forms, Validation, Responsive) | ⏳ PENDING | Frontend Designer | 8-10h | → All Done |

**Total Estimated Hours**: 80-102h (3-4 weeks full-time, including reorganization)

---

## ✅ Phase 0: Reorganização Monorepo (Pré-requisito)

### Task A0 - Reorganizar para Monorepo (/backend + /frontend) ⏳

**Objetivo**: Separar código Python e JavaScript em estrutura monorepo profissional.

**Acceptance Criteria**:
- [ ] `/backend/` contém todo código Python (app/, worker/, tests/, alembic/, etc)
- [ ] `/frontend/` criado vazio (pronto para Next.js)
- [ ] `.gitignore` atualizado com node_modules patterns
- [ ] `docker-compose.yml` atualizado com paths corretos
- [ ] Backend roda em `http://localhost:8000` (sem dependências relativas)
- [ ] README.md atualizado com instruções separadas

**Commands**:
```bash
# 1. Criar diretório backend
mkdir backend

# 2. Mover código Python
mv app/ backend/
mv worker/ backend/
mv tests/ backend/
mv alembic/ backend/
mv alembic.ini backend/
mv main.py backend/
mv run_migrations.py backend/
mv requirements.txt backend/

# 3. Criar .env.backend
cp .env backend/.env
cp .env.example backend/.env.example

# 4. Criar frontend/ (vazio por enquanto)
mkdir frontend

# 5. Atualizar docker-compose.yml → paths: ./backend/, ./frontend/
# 6. Atualizar .gitignore → backend/node_modules, frontend/.next, etc
# 7. Atualizar README.md → instruções separadas
```

**Files to Update**:
- `.gitignore` — adicionar `/backend/node_modules`, `/frontend/node_modules`, `/frontend/.next`
- `docker-compose.yml` — referências para `./backend/`
- `README.md` — seções separadas Backend Setup vs Frontend Setup
- `.github/workflows/` — paths

**Git Commit Message**:
```
refactor: Reorganize into monorepo structure with /backend and /frontend

- Move Python code to backend/ (app/, worker/, tests/, alembic/, main.py)
- Create frontend/ directory (ready for Next.js)
- Update docker-compose.yml paths
- Update .gitignore patterns
- Update README.md with separate setup instructions
- Backend still runs independently: http://localhost:8000

Files moved:
- app/ → backend/app/
- worker/ → backend/worker/
- tests/ → backend/tests/
- alembic/ → backend/alembic/
- main.py → backend/main.py
- requirements.txt → backend/requirements.txt

Structure:
- conektabots/backend/  ← Python + FastAPI
- conektabots/frontend/ ← Next.js (coming)

Tests: Backend still starts ✅ → uvicorn main:app
Next: Task A1 - Setup Next.js
```

---



### Task A1 - Setup Next.js 15 + Auth Infrastructure 🔄

**Objetivo**: Criar base funcional com Next.js 15, TypeScript, Tailwind, Supabase Client removido, JWT management, e estrutura de pastas.

**Acceptance Criteria**:
- [ ] `npm run dev` inicia sem erros
- [ ] Roteamento funciona (/ → landing, /dashboard → autenticado)
- [ ] JWT tokens armazenados em localStorage
- [ ] Axios/fetch wrapper pronto com interceptadores
- [ ] TypeScript strict mode ativo
- [ ] Tailwind CSS funcionando (componentes estilizados)
- [ ] Estrutura de pastas organizada

**Files to Create**:
```
frontend/
├── app/
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Landing page (/)
│   ├── (auth)/
│   │   ├── layout.tsx        # Auth layout
│   │   ├── login/page.tsx    # /login (stub)
│   │   └── signup/page.tsx   # /signup (stub)
│   ├── (dashboard)/
│   │   ├── layout.tsx        # Dashboard layout (sidebar + header)
│   │   └── page.tsx          # /dashboard (stub with stats)
│   ├── api/                  # API routes (none yet)
│   └── globals.css           # Tailwind globals
├── lib/
│   ├── api.ts                # Axios wrapper + interceptors
│   ├── auth.ts               # JWT token helpers
│   ├── constants.ts          # API URLs, constants
│   └── types.ts              # TypeScript types
├── hooks/
│   ├── useAuth.ts            # Auth context hook
│   ├── useApi.ts             # API wrapper hook
│   └── useToast.ts           # Toast notifications
├── middleware.ts             # Next.js middleware (redirect /dashboard → /login)
├── .env.local                # Environment variables
├── .env.example              # Template
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── next.config.ts            # Next.js configuration
├── tailwind.config.ts        # Tailwind configuration
└── postcss.config.js         # PostCSS configuration
```

**Commands to Run**:
```bash
# Create Next.js project
npx create-next-app@latest frontend --typescript --tailwind --eslint --app

# Move into directory
cd frontend

# Install additional dependencies
npm install axios zustand react-hot-toast

# Start dev server
npm run dev

# Verify http://localhost:3000 loads
```

**Code to Implement**:

1. **lib/constants.ts** - API URLs
2. **lib/api.ts** - Axios wrapper with JWT interceptor
3. **lib/auth.ts** - JWT token helpers
4. **hooks/useAuth.ts** - Auth context
5. **middleware.ts** - Protected routes
6. **app/layout.tsx** - Root layout
7. **app/page.tsx** - Landing page (stub)
8. **app/(auth)/layout.tsx & pages** - Auth pages (stubs)
9. **app/(dashboard)/layout.tsx & page.tsx** - Dashboard (stubs)

**Git Commit Message**:
```
feat: Initialize Next.js 15 frontend with auth infrastructure

- Create Next.js 15 project with TypeScript + Tailwind CSS
- Implement JWT token management (localStorage + refresh)
- Setup Axios wrapper with auto-refresh interceptor on 401
- Create auth context hook + middleware for protected routes
- Folder structure: lib/, hooks/, app/
- Landing page stub + auth pages stubs + dashboard stub
- .env.local template for API_URL configuration
- Todo: Backend CORS validation + password hashing

Files:
- frontend/ (new project root)
- lib/api.ts, auth.ts, constants.ts, types.ts
- hooks/useAuth.ts
- middleware.ts
- app/layout.tsx, page.tsx + (auth)/ + (dashboard)/

Dependencies added:
- axios (HTTP client)
- zustand (state management)
- react-hot-toast (notifications)

Tests: npm run dev ✅ → http://localhost:3000 loads
Next: Task A2 - Backend CORS validation
```

---

### Task A2 - Backend Validation (CORS + Endpoints) ⏳

**Objetivo**: Validar que backend está pronto para consumição pelo frontend (CORS, endpoints, error handling).

**Acceptance Criteria**:
- [ ] CORS_ORIGINS inclui `http://localhost:3000` (dev)
- [ ] POST `/api/v1/auth/login` → retorna access_token + refresh_token
- [ ] POST `/api/v1/auth/signup` → cria session + tokens
- [ ] POST `/api/v1/auth/refresh` → novo access_token
- [ ] GET `/api/v1/bots` com token válido → lista bots
- [ ] GET `/api/v1/marketplaces` → lista integrações
- [ ] Response format padronizado (JSON)
- [ ] Error responses têm status codes corretos (400, 401, 403, 404, 500)

**Validation Steps**:
```bash
# 1. Check CORS_ORIGINS in app/core/config.py
grep -i "CORS_ORIGINS" app/core/config.py

# 2. Test signup endpoint
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test"}'

# 3. Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# 4. Test protected endpoint (using token from login)
curl -X GET http://localhost:8000/api/v1/bots \
  -H "Authorization: Bearer {ACCESS_TOKEN}"

# 5. Test refresh endpoint
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"{REFRESH_TOKEN}"}'
```

**Git Commit Message**:
```
fix: Add CORS support for localhost:3000 frontend dev server

- Update CORS_ORIGINS in app/core/config.py to include http://localhost:3000
- Verify endpoints (login, signup, refresh, bots, marketplaces) respond correctly
- Validate error handling returns proper HTTP status codes
- Document expected request/response formats
- Tested with curl: signup ✅ → login ✅ → protected endpoint ✅

Files:
- app/core/config.py (CORS settings)

Tests: All endpoints responding correctly ✅
Next: Task B1 - Frontend auth pages
```

---

## 🔐 Phase 2: Authentication (Semana 1-2)

### Task B1 - Auth Pages (Login/Signup/Protected Routes) ⏳

**Objetivo**: Implementar páginas de login e signup com fluxo de autenticación completo.

**Acceptance Criteria**:
- [ ] `/login` page carrega com formulário (email + password)
- [ ] `/signup` page carrega com formulário (name + email + password)
- [ ] Submit forms chama FastAPI endpoints
- [ ] Tokens armazenados em localStorage ao login bem-sucedido
- [ ] Redirecionamento automático: logged in → /dashboard, not logged in → /login
- [ ] Token refresh automático no 401 (axios interceptor)
- [ ] Logout limpa localStorage + redireciona /login
- [ ] Form validation (email format, password strength)
- [ ] Error messages amigáveis (user-facing)

**Files to Create**:
```
frontend/app/(auth)/
├── layout.tsx
├── login/
│   └── page.tsx
└── signup/
    └── page.tsx

frontend/components/
└── (auth forms — se reutilizáveis)
```

**Acceptance Verification**:
```bash
1. npm run dev
2. Navigate to http://localhost:3000/login
3. Try login with invalid credentials → error message
4. Try login with valid credentials → redirects /dashboard
5. Close browser, reopen → still authenticated (token in localStorage)
6. Token expires (or manually clear) → 401 → auto-refresh
7. Logout button → clears localStorage + redirects /login
```

**Git Commit**:
```
feat: Implement authentication pages (login/signup) with token management

- Create /login page with email + password form
- Create /signup page with name + email + password form
- Implement JWT token storage in localStorage
- Add middleware to protect /dashboard routes
- Axios interceptor auto-refreshes tokens on 401
- Form validation (email, password strength)
- Error handling with user-friendly messages
- Logout clears tokens and redirects to /login

Files:
- app/(auth)/layout.tsx
- app/(auth)/login/page.tsx
- app/(auth)/signup/page.tsx
- middleware.ts (updated)
- lib/api.ts (updated with refresh interceptor)

Tests:
- Login flow works ✅
- Signup creates new account ✅
- Token refresh on 401 ✅
- Protected routes redirect to /login ✅
- Logout works ✅

Next: Task C1 - Dashboard layout
```

---

## 📊 Phase 3: Dashboard Core (Semana 2)

### Task C1 - Dashboard Layout Base ⏳

**Objetivo**: Criar layout base do dashboard com sidebar, header, e stats.

**Acceptance Criteria**:
- [ ] Sidebar navigation com links (Bots, Regras, Agendamentos, Marketplaces, Logs, Settings)
- [ ] Header com user profile + logout
- [ ] Stats section (bots count, rules count, last logs)
- [ ] Responsive layout (mobile: hamburger menu, desktop: sidebar)
- [ ] Breadcrumbs na página
- [ ] Loading states
- [ ] Dark mode toggle (opcional)

**Files to Create**:
```
frontend/app/(dashboard)/
├── layout.tsx              # Dashboard layout com sidebar + header
└── page.tsx                # Dashboard home com stats

frontend/components/
├── Sidebar.tsx
├── Header.tsx
├── StatsCard.tsx
└── (outros componentes reutilizáveis)
```

**Git Commit**:
```
feat: Build responsive dashboard layout with sidebar navigation

- Create dashboard layout wrapper with sidebar + header
- Implement user profile dropdown in header
- Add navigation links (bots, rules, schedules, marketplaces, logs, settings)
- Fetch and display dashboard stats (bots count, rules, last execution)
- Responsive design: mobile hamburger menu + desktop permanent sidebar
- Breadcrumb navigation on all pages
- Loading skeleton states while fetching data

Files:
- app/(dashboard)/layout.tsx
- app/(dashboard)/page.tsx
- components/Sidebar.tsx
- components/Header.tsx
- components/StatsCard.tsx

Tests:
- Layout renders ✅
- Navigation links work ✅
- Stats fetch from API ✅
- Mobile responsive ✅

Next: Task D1-D6 - CRUD pages (paralelo)
```

---

## 🗂️ Phase 4: CRUD Pages (Semana 2-3 - PARALELO)

### Task D1 - Bots Management CRUD ⏳

**Objetivo**: Tabela, criar, editar, deletar bots.

**Acceptance Criteria**:
- [ ] GET `/dashboard/bots` lista todos os bots em tabela
- [ ] POST criar novo bot (form: name, api_id, api_hash, phone)
- [ ] PATCH editar bot existente
- [ ] DELETE soft-delete bot (com confirmação)
- [ ] Toggle bot ativo/inativo
- [ ] Paginação (se mais de 20 bots)
- [ ] Loading states + error messages

---

### Task D2 - Rules Management CRUD (Complex Form) ⏳

**Objetivo**: Tabela, criar/editar regras com step-by-step form.

**Acceptance Criteria**:
- [ ] GET `/dashboard/regras` lista com paginação
- [ ] Step 1: Selecionar bot
- [ ] Step 2: Selecionar chats origem (input + autocomplete)
- [ ] Step 3: Selecionar chats destino
- [ ] Step 4: Selecionar marketplace (opcional)
- [ ] Step 5: Adicionar filtros (dinâmico — add/remove)
- [ ] Step 6: Adicionar condições (whitelist/blacklist)
- [ ] Step 7: Tipo mídia (todos, foto, vídeo, etc.)
- [ ] Review + submit
- [ ] Edit regra existente (pré-populate steps)
- [ ] Delete com confirmação

---

### Task D3 - Schedules Management CRUD (Complex Form) ⏳

**Objetivo**: Similar a D2 mas para agendamentos.

**Acceptance Criteria**:
- [ ] GET `/dashboard/agendamentos` lista
- [ ] Step 1: Bot selection
- [ ] Step 2-3: Chats origem/destino
- [ ] Step 4: Horários (time picker — múltiplos)
- [ ] Step 5: Filtros + condições
- [ ] Step 6: Tipo envio (sequencial, pontual)
- [ ] Step 7: Envio manual button
- [ ] Delete com confirmação

---

### Task D4 - Marketplaces CRUD (Dynamic Forms) ⭐ ⏳

**Objetivo**: Integrar marketplaces com formulários dinâmicos.

**Acceptance Criteria**:
- [ ] GET `/dashboard/marketplaces` lista integrações
- [ ] Modal: Selecionar tipo (Shopee, ML, Amazon, Magalu)
- [ ] Dynamic form fields (diferentes por marketplace)
- [ ] POST Create integration → encrypted storage
- [ ] Test connection button → POST `/marketplaces/{id}/test`
- [ ] PATCH Update credenciais (re-encrypt)
- [ ] DELETE soft-delete
- [ ] Status indicador (ativo/inativo/teste failed)

---

### Task D5 - Logs Viewer (Table + Filters + Export) ⏳

**Objetivo**: Dashboard de logs com paginação e filtros.

**Acceptance Criteria**:
- [ ] GET `/dashboard/logs` tabela paginada (100/página)
- [ ] Colunas: Data/hora, Bot, Origem, Destino, Status, Mensagem
- [ ] Filtros: Status (sucesso/erro/bloqueado), Bot, Date range
- [ ] Search global
- [ ] Export CSV
- [ ] Log detail modal
- [ ] Auto-refresh (poll 5s)

---

### Task D6 - Settings & Account Management ⏳

**Objetivo**: Página de configurações.

**Acceptance Criteria**:
- [ ] `/dashboard/configuracoes` carrega
- [ ] Account tab: profile (nome, email, foto), change password, delete account
- [ ] Team tab: invite members, manage roles (owner/admin/editor/viewer), remove
- [ ] Billing tab: current plan, usage stats (bots, rules, msgs/hour), upgrade button

---

## 🎨 Phase 5: Landing Page (Semana 3 - PARALELO)

### Task E1 - Marketing Landing Page ⏳

**Objetivo**: Homepage com marketing content.

**Acceptance Criteria**:
- [ ] Hero section com CTA ("Get Started")
- [ ] Features section (telegram, marketplaces, automation, rules)
- [ ] Pricing table (Free, Starter, Pro, Enterprise)
- [ ] Testimonials (fake se necessário)
- [ ] FAQ section
- [ ] Footer com links
- [ ] Responsive design
- [ ] /pricing page (opcional)

---

## 🎨 Phase 6: Polish & UX (Final Week)

### Task F1 - Polish & UX (Forms, Validation, Responsive) ⏳

**Objetivo**: Qualidade final, acessibilidade, performance.

**Acceptance Criteria**:
- [ ] Todos forms têm validação clara (inline errors)
- [ ] Loading states em todos os places (skeletons, spinners)
- [ ] Error boundaries (catch crashes gracefully)
- [ ] Toast notifications (success, error, info)
- [ ] Responsive design QA (mobile, tablet, desktop)
- [ ] Accessibility (ARIA labels, focus management)
- [ ] Performance (lazy loading, code splitting)
- [ ] No console errors/warnings
- [ ] Dark mode works everywhere (opcional)

---

## 📈 Progress Tracking

Update this table as you complete tasks:

| Task | Status | Commit | Date | Notes |
|------|--------|--------|------|-------|
| A0 - Monorepo Reorg | ⏳ PENDING | - | - | Move to /backend + /frontend |
| A1 - Setup Next.js | ⏳ PENDING | - | - | Starting after A0 |
| A2 - Backend CORS | ⏳ PENDING | - | - | After A1 |
| B1 - Auth Pages | ⏳ PENDING | - | - | After A2 |
| C1 - Dashboard Layout | ⏳ PENDING | - | - | After B1 |
| D1 - Bots CRUD | ⏳ PENDING | - | - | Paralelo com D2-D6 |
| D2 - Rules CRUD | ⏳ PENDING | - | - | Paralelo com D1,D3-D6 |
| D3 - Schedules CRUD | ⏳ PENDING | - | - | Paralelo com D1-D2,D4-D6 |
| D4 - Marketplaces CRUD | ⏳ PENDING | - | - | Paralelo com D1-D3,D5-D6 |
| D5 - Logs Viewer | ⏳ PENDING | - | - | Paralelo com D1-D4,D6 |
| D6 - Settings & Billing | ⏳ PENDING | - | - | Paralelo com D1-D5 |
| E1 - Landing Page | ⏳ PENDING | - | - | Paralelo com D1-D6 |
| F1 - Polish & UX | ⏳ PENDING | - | - | After all above |

---

## 🚀 Deployment Checklist

Before deploying to Vercel:

- [ ] All tasks completed and tested
- [ ] No console errors
- [ ] Environment variables ready (.env.production)
- [ ] API_URL points to production backend
- [ ] CORS on backend includes production domain
- [ ] All tests pass
- [ ] Performance optimized (Lighthouse > 80)
- [ ] Accessibility checked (WAVE, axe DevTools)

**Deployment Command**:
```bash
# 1. Push to GitHub
git push origin feature/frontend-phase3

# 2. Create PR / Merge to main
# 3. Vercel auto-deploys from GitHub

# Vercel Dashboard:
# - Connect repository
# - Set NEXT_PUBLIC_API_URL environment variable
# - Deploy!
```

---

**Last Updated**: Abril 15, 2026  
**Owner**: Frontend Designer Agent  
**Roadmap Ref**: `.project/roadmap.md` (Fase 3)
