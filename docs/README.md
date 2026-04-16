# 📚 Documentação - ConektaBots API

Bem-vindo à documentação do ConektaBots! Esta pasta contém guias e referências para desenvolvedores.

## 📂 Estrutura

### 📖 `/guides/` - Guias de Desenvolvimento

Tutoriais e guias passo-a-passo para tarefas comuns:

- **[TESTING_GUIDE.md](guides/TESTING_GUIDE.md)** - Como testar os endpoints da API
  - Teste automático com pytest
  - Teste simplificado  
  - Teste manual com script Python
  - Exemplos com cURL

- **[FIX_REGISTER_ERROR_500.md](guides/FIX_REGISTER_ERROR_500.md)** - Correção do erro 500 no registro
  - Problema identificado
  - Solução implementada
  - Migrações de banco de dados
  - Testes recomendados

### 🔌 `/api/` - Referência de API

Documentação técnica sobre a API:

- **[TEST_RESULTS.md](api/TEST_RESULTS.md)** - Resultados dos testes dos endpoints
  - Endpoints funcionando
  - Endpoints com problemas
  - Casos de teste

## 🚀 Quick Start

### 1. Testar Endpoints
```bash
# Opção 1: Script automático
python test_endpoints_manual.py

# Opção 2: Pytest
pytest tests/test_endpoints_simple.py -v

# Opção 3: cURL
curl http://localhost:8000/healthz
```

### 2. Entender a Autenticação
Veja [FIX_REGISTER_ERROR_500.md](guides/FIX_REGISTER_ERROR_500.md) para:
- Fluxo de registro
- Estrutura do banco de dados
- JWT tokens

### 3. Resolver Problemas
Cada guia contém seção de troubleshooting.

## 📋 Índice Completo

### Testes
- [TESTING_GUIDE.md](guides/TESTING_GUIDE.md) - Guia completo de testes
- [TEST_RESULTS.md](api/TEST_RESULTS.md) - Resultados e recomendações

### Fixes & Correções
- [FIX_REGISTER_ERROR_500.md](guides/FIX_REGISTER_ERROR_500.md) - Erro 500 no registro

## 💡 Dicas

- Use `Ctrl+F` ou `Cmd+F` para buscar por keywords
- Links estão em markdown: `[titulo](path)`
- Exemplos de código estão em blocos ` ``` `

## 🔄 Atualizações

Quando novos guias forem adicionados, eles aparecerão aqui.

**Última atualização**: 2026-04-15
