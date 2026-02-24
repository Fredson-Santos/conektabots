# ConektaBots 🚀

ConektaBots é uma plataforma robusta para gerenciamento e automação de bots do Telegram. Com uma interface web intuitiva, você pode administrar múltiplos bots, configurar regras de encaminhamento complexas, agendar postagens e monitorar tudo em tempo real.

## ✨ Funcionalidades

- **Gestão de Múltiplos Bots**: Suporte para Userbots (contas pessoais) e Bots API.
- **Regras de Encaminhamento Inteligentes**:
  - Filtros por **Whitelist** e **Blacklist** de palavras.
  - **Substituição de Texto** automática em mensagens encaminhadas.
  - Toggles individuais para ativar/desativar regras rapidamente.
- **Agendamentos**: Planeje postagens para canais e grupos com suporte a mídias.
- **Painel Administrativo**: Interface web moderna construída com FastAPI e Jinja2.
- **Monitoramento**: Logs detalhados de execução e histórico de tarefas.
- **Resiliência**: Gerenciamento automático de sessões e reconexão.

## 🛠️ Tecnologias Principais

- **Backend**: Python 3.10+, FastAPI
- **Bot Framework**: Telethon (Telegram MTProto)
- **Banco de Dados**: SQLModel (SQLAlchemy) + SQLite
- **Migrações**: Alembic
- **Template Engine**: Jinja2
- **Containerização**: Docker & Docker Compose

## 🚀 Como Começar

### Pré-requisitos
- Python 3.10 ou superior
- Docker (opcional, recomendado para deploy)

### Instalação Manual

1. **Clone o repositório e instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure as variáveis de ambiente:**
   Copie o arquivo `.env.example` para `.env` e ajuste conforme necessário.

3. **Inicie o Banco de Dados (Migrações):**
   ```bash
   alembic upgrade head
   ```

4. **Inicie os serviços:**
   - **Painel Web:** `uvicorn main:app --reload`
   - **Gerenciador de Bots:** `python manager.py`

### Rodando com Docker (Recomendado)

A maneira mais fácil de rodar o ConektaBots é via Docker Compose:

```bash
docker-compose up -d --build
```

O painel ficará disponível em `http://localhost:8005` (ou na porta configurada no seu `.env`).

## 📁 Estrutura do Projeto

- `main.py`: API e interface web (painel administrativo).
- `manager.py`: Ponto de entrada para os bots; inicia as instâncias ativas.
- `worker.py`: Lógica principal de processamento de mensagens e tarefas.
- `database.py`: Definição de modelos e esquemas de dados.
- `alembic/`: Gerenciamento de versões do banco de dados.
- `templates/`: Interface visual do sistema.

## 📝 Notas de Desenvolvimento

- Utilize o script `adicionar_bot.py` via CLI caso prefira não usar a interface web inicialmente.
- Atas de migração devem ser criadas sempre que houver mudanças no arquivo `database.py` usando:
  ```bash
  alembic revision --autogenerate -m "descrição da mudança"
  ```

---
Desenvolvido para automação eficiente e escalável no Telegram.
