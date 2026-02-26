# ConektaBots 🚀

ConektaBots é uma plataforma robusta e elegante para gerenciamento e automação de bots do Telegram. Com uma interface web intuitiva, você pode administrar múltiplos bots, configurar regras de encaminhamento complexas, agendar postagens com filtros avançados e monitorar tudo em tempo real.

## ✨ Funcionalidades

- **Gestão de Múltiplos Bots**: Suporte completo para Userbots (contas pessoais) e Bots API.
- **Regras de Encaminhamento Inteligentes**:
  - Filtros por **Whitelist** e **Blacklist** de palavras.
  - **Substituição de Texto** automática em mensagens encaminhadas.
  - Toggles (Ativar/Desativar) individuais para controle instantâneo.
- **Agendamentos Avançados**:
  - Planeje postagens para canais e grupos com suporte a mídias.
  - Filtros de conteúdo (Whitelist/Blacklist) e substituição de texto aplicados aos agendamentos.
  - Gerenciamento de status (Ativo/Inativo) por agendamento.
- **Painel Administrativo Premium**: Interface web moderna construída com FastAPI, Jinja2 e CSS customizado.
- **Monitoramento e Resiliência**:
  - Logs detalhados de execução e histórico de tarefas.
  - Gerenciamento automático de sessões e fluxo de login seguro (incluindo 2FA).

## 🛠️ Tecnologias Principais

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Bot Framework**: [Telethon](https://docs.telethon.dev/) (Telegram MTProto)
- **Banco de Dados**: [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
- **Migrações**: [Alembic](https://alembic.sqlalchemy.org/)
- **Frontend**: Jinja2 Templates + Vanilla CSS (Design Moderno)
- **Containerização**: Docker & Docker Compose

## 🚀 Como Começar

### Pré-requisitos
- Python 3.10 ou superior
- Docker & Docker Compose (Recomendado para produção)

### Instalação Manual

1. **Clone o repositório e instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure as variáveis de ambiente:**
   Copie o arquivo `.env.example` para `.env` e preencha suas chaves de API do Telegram (`TG_API_ID`, `TG_API_HASH`).

3. **Inicie o Banco de Dados:**
   ```bash
   alembic upgrade head
   ```

4. **Inicie os serviços:**
   - **Painel Web:** `uvicorn main:app --host 127.0.0.1 --port 8000 --reload`
   - **Gerenciador de Bots:** `python manager.py`

### Rodando com Docker (Recomendado)

O ConektaBots já vem configurado para um deploy rápido:

```bash
docker-compose up -d --build
```
O painel ficará disponível em `http://localhost:8000` (ou na porta configurada).

## 📁 Estrutura do Projeto

- `main.py`: Ponto de entrada da aplicação FastAPI.
- `manager.py`: Orquestrador de processos dos bots.
- `worker.py`: Coração do processamento de mensagens e lógica de encaminhamento.
- `app/`:
  - `models/`: Modelos SQLModel (Bots, Regras, Agendamentos, Logs).
  - `routers/`: Rotas da API e da interface web.
  - `services/`: Lógica de negócio e integração com Telegram.
- `templates/`: Arquivos HTML/Jinja2 para a interface web.
- `alembic/`: Scripts de migração do banco de dados.

---
Desenvolvido para automação eficiente e escalável no Telegram.

