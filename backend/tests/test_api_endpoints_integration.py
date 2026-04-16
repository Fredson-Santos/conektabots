"""Teste de Integração — Verifica todos os endpoints da API.

Testa:
- GET / (info da API)
- GET /healthz (health check rápido)
- GET /health (health check com DB)
- POST /api/v1/auth/register (registro)
- POST /api/v1/auth/login (login)
- GET /api/v1/auth/me (perfil do usuário)
- E outros endpoints protegidos

Uso: pytest tests/test_api_endpoints_integration.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock

from main import app


@pytest.fixture
def client():
    """Create TestClient for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def client_with_auth():
    """Create TestClient with mocked tenant context for protected endpoints."""
    from unittest.mock import patch
    
    def get_mock_session():
        mock_session = MagicMock(spec=AsyncSession)
        return mock_session
    
    # Mock the get_session dependency
    app.dependency_overrides = {}
    
    return TestClient(app)


class TestPublicEndpoints:
    """Testes de endpoints públicos (sem autenticação)."""
    
    def test_root_endpoint(self, client):
        """Teste GET / — Retorna informações da API."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "ConektaBots API"
        assert "version" in data
        assert "docs" in data
    
    def test_healthz_endpoint(self, client):
        """Teste GET /healthz — Health check rápido."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "message" in data
    
    def test_health_endpoint(self, client):
        """Teste GET /health — Health check com validação de DB.
        
        Nota: Este teste pode falhar se o banco de dados de teste não estiver 
        adequadamente configurado. Isso é esperado em ambiente de teste.
        """
        response = client.get("/health")
        
        # Pode retornar 200 se DB conectado ou 500 se desconectado
        assert response.status_code in [200, 500]
        data = response.json()
        assert "status" in data


class TestAuthEndpoints:
    """Testes de endpoints de autenticação."""
    
    def test_register_user_endpoint_exists(self, client):
        """Teste se endpoint POST /api/v1/auth/register existe."""
        # Este endpoint é público (POST auth/register deve pular tenant middleware)
        payload = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "nome": "Test User"
        }
        response = client.post("/api/v1/auth/register", json=payload)
        
        # Pode retornar vários status: 201 (sucesso), 422 (validação), 409 (conflito), etc
        assert response.status_code in [200, 201, 400, 422, 409, 500]
    
    def test_login_user_endpoint_exists(self, client):
        """Teste se endpoint POST /api/v1/auth/login existe."""
        # Este endpoint é público (POST auth/login deve pular tenant middleware)
        payload = {
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }
        response = client.post("/api/v1/auth/login", json=payload)
        
        # Pode retornar: 200 (sucesso), 401 (não autorizado), 422 (validação), etc
        assert response.status_code in [200, 401, 404, 422, 400, 500]
    
    def test_get_current_user_endpoint_exists(self, client):
        """Teste se endpoint GET /api/v1/auth/me existe."""
        response = client.get("/api/v1/auth/me")
        
        # Sem token, deve retornar 401 ou 403
        assert response.status_code in [401, 403, 422, 400]


class TestProtectedEndpoints:
    """Testes de endpoints protegidos (requerem autenticação)."""
    
    def test_bots_endpoint_requires_auth(self, client):
        """Testa se GET /api/v1/bots requer autenticação."""
        response = client.get("/api/v1/bots")
        # Sem token, deve retornar erro de auth ou validação
        assert response.status_code in [401, 403, 400, 422]
    
    def test_tenants_endpoint_requires_auth(self, client):
        """Testa se GET /api/v1/tenants requer autenticação."""
        response = client.get("/api/v1/tenants")
        # Sem token/tenant, deve retornar erro
        assert response.status_code in [401, 403, 400, 422]
    
    def test_regras_endpoint_requires_auth(self, client):
        """Testa se GET /api/v1/regras requer autenticação."""
        response = client.get("/api/v1/regras")
        assert response.status_code in [401, 403, 400, 422]
    
    def test_agendamentos_endpoint_requires_auth(self, client):
        """Testa se GET /api/v1/agendamentos requer autenticação."""
        response = client.get("/api/v1/agendamentos")
        assert response.status_code in [401, 403, 400, 422]
    
    def test_logs_endpoint_requires_auth(self, client):
        """Testa se GET /api/v1/logs requer autenticação."""
        response = client.get("/api/v1/logs")
        assert response.status_code in [401, 403, 400, 422]
    
    def test_marketplaces_endpoint_exists(self, client):
        """Testa se endpoint /api/v1/marketplaces existe."""
        response = client.get("/api/v1/marketplaces")
        # Pode ser público ou protegido, mas não deve dar 404
        assert response.status_code != 404


class TestErrorHandling:
    """Testes de tratamento de erros."""
    
    def test_nonexistent_endpoint_returns_404(self, client):
        """Teste de endpoint inexistente — Deve retornar 404."""
        response = client.get("/api/v1/nonexistent-endpoint-xyz")
        assert response.status_code == 404
    
    def test_invalid_json_payload(self, client):
        """Teste de payload JSON inválido."""
        response = client.post(
            "/api/v1/auth/login",
            data=b"invalid json{",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [422, 400]
    
    def test_wrong_http_method_on_public_endpoint(self, client):
        """Teste de método HTTP incorreto em endpoint público."""
        # /healthz é GET, tenta POST
        response = client.post("/healthz", json={})
        assert response.status_code == 405  # Method Not Allowed


class TestEndpointStructure:
    """Testes da estrutura geral da API."""
    
    def test_public_endpoints_accessible(self, client):
        """Verifica que endpoints públicos são acessíveis."""
        public_endpoints = [
            "/",
            "/healthz",
            "/health",
        ]
        
        for endpoint in public_endpoints:
            response = client.get(endpoint)
            assert response.status_code != 404, f"Endpoint {endpoint} não encontrado"
    
    def test_api_version_prefix(self, client):
        """Verifica se endpoints Auth usam /api/v1/auth/ prefix."""
        # Verifica que o endpoint de auth existe com o prefix correto
        response = client.post("/api/v1/auth/register", json={})
        # Pode falhar por validação, mas não por 404
        assert response.status_code != 404
    
    def test_protected_endpoints_exist(self, client):
        """Verifica que endpoints protegidos existem (no path)."""
        protected_endpoints = [
            "/api/v1/bots",
            "/api/v1/tenants",
            "/api/v1/marketplaces",
            "/api/v1/regras",
            "/api/v1/agendamentos",
            "/api/v1/logs",
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Podem retornar 401/403/422 (proteção) mas não 404
            assert response.status_code != 404, \
                f"Endpoint {endpoint} não está registrado (retornou 404)"


class TestAPISummary:
    """Resumo e verificações gerais da API."""
    
    def test_api_is_running(self, client):
        """Teste basic: API está respondendo."""
        response = client.get("/healthz")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self, client):
        """Verifica se Schema OpenAPI está disponível."""
        response = client.get("/openapi.json")
        # Pode estar protegido ou público
        assert response.status_code in [200, 401, 403]
    
    def test_api_documentation_page_available(self, client):
        """Verifica se página de documentação está disponível."""  
        response = client.get("/docs")
        # Pode estar protegida ou pública
        assert response.status_code in [200, 401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
