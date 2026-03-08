# ConektaBots 🚀

ConektaBots é uma plataforma robusta e elegante para gerenciamento e automação de bots do Telegram. Com uma interface web intuitiva, você pode administrar múltiplos bots, configurar regras de encaminhamento complexas, agendar postagens com filtros avançados e monitorar tudo em tempo real.

## ✨ Funcionalidades

- **Gestão de Múltiplos Bots**: Suporte completo para Userbots (contas pessoais) e Bots API.
- **Regras de Encaminhamento Inteligentes**:
  - Filtros por **Whitelist** e **Blacklist** de palavras.
  - **Substituição de Texto** automática em mensagens encaminhadas.
  - Filtro por tipo de mídia (foto, vídeo, texto).
  - Conversão automática de links Shopee (afiliados).
  - Toggles (Ativar/Desativar) individuais para controle instantâneo.
- **Agendamentos Avançados**:
  - Planeje postagens para canais e grupos com suporte a mídias.
  - Modos de envio: sequencial (auto-incremento) ou pontual.
  - Filtros de conteúdo (Whitelist/Blacklist) e substituição de texto aplicados aos agendamentos.
  - Gerenciamento de status (Ativo/Inativo) por agendamento.
- **Painel Administrativo**: Interface web moderna com HTMX para atualizações em tempo real.
- **Monitoramento e Resiliência**:
  - Logs detalhados de execução e histórico de tarefas.
  - Hot-reload de regras (sem reiniciar o bot).
  - Gerenciamento automático de sessões e fluxo de login seguro (incluindo 2FA).

## 🛠️ Tecnologias Principais

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Bot Framework**: [Telethon](https://docs.telethon.dev/) (Telegram MTProto)
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
- **Banco de Dados**: [PostgreSQL](https://www.postgresql.org/) 16
- **Migrações**: [Alembic](https://alembic.sqlalchemy.org/)
- **Frontend**: Jinja2 Templates + HTMX + CSS
- **Containerização**: Docker & Docker Compose

## 🚀 Como Começar

### Pré-requisitos
- Python 3.10 ou superior
- Docker & Docker Compose (Recomendado para produção)
- PostgreSQL 16 (ou via Docker)

### Rodando com Docker (Recomendado)

O ConektaBots já vem com Docker Compose configurado com 3 serviços: **PostgreSQL**, **Web** e **Manager**.

1. **(Opcional) Configure as variáveis de ambiente** criando um arquivo `.env`:
   ```env
   WEB_PORT=8005
   TZ=America/Sao_Paulo
   POSTGRES_USER=conekta
   POSTGRES_PASSWORD=conekta
   POSTGRES_DB=conektabots
   ```

2. **Suba os containers:**
   ```bash
   docker compose up --build -d
   ```

3. O painel ficará disponível em `http://seu-servidor:8005`.

> As migrações do banco são executadas automaticamente ao iniciar o container web.

### Instalação Manual (Desenvolvimento)

1. **Clone o repositório e instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure a variável de ambiente do banco:**
   ```bash
   export DATABASE_URL=postgresql://conekta:conekta@localhost:5432/conektabots
   ```

3. **Execute as migrações:**
   ```bash
   alembic upgrade head
   ```

4. **Inicie os serviços:**
   ```bash
   # Terminal 1 - Painel Web
   uvicorn main:app --host 127.0.0.1 --port 8000

   # Terminal 2 - Gerenciador de Bots
   python manager.py
   ```

## 📁 Estrutura do Projeto

```
├── main.py            # Ponto de entrada da aplicação FastAPI
├── manager.py         # Orquestrador que inicia workers para cada bot ativo
├── worker.py          # Engine async de processamento (regras, filas, agendamentos)
├── app/
│   ├── core/          # Configuração, banco de dados, dependências
│   ├── models/        # Modelos SQLModel (Bot, Regra, Agendamento, Log, Config)
│   ├── routers/       # Rotas da API e interface web
│   ├── schemas/       # Schemas Pydantic (DTOs)
│   └── services/      # Lógica de negócio
├── templates/         # Arquivos HTML/Jinja2 para a interface web
├── alembic/           # Scripts de migração do banco de dados
└── docker-compose.yml # Orquestração: PostgreSQL + Web + Manager
```

## 🐳 Arquitetura Docker

| Container | Serviço | Descrição |
|-----------|---------|-----------|
| `conekta_db` | PostgreSQL 16 | Banco de dados persistente |
| `conekta_web` | FastAPI + Uvicorn | Painel web (porta 8005) |
| `conekta_manager` | Python | Orquestrador dos bots Telegram |

Os containers seguem a ordem: **db** → **web** (roda migrações) → **manager**.

---
Desenvolvido para automação eficiente e escalável no Telegram

