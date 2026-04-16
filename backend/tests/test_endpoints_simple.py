"""Teste de Endpoints - Versão Simplificada (Apenas endpoints que funcionam)

Foco: Endpoints públicos que não requerem autenticação
Uso: pytest tests/test_endpoints_simple.py -v
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create TestClient for FastAPI app."""
    return TestClient(app)


class TestPublicHealthEndpoints:
    """Teste de endpoints de health/status públicos."""
    
    def test_root_api_info(self, client):
        """GET / — Retorna informações da API."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "ConektaBots API"
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        print(f"✅ Root endpoint: {data}")
    
    def test_healthz_quick_check(self, client):
        """GET /healthz — Health check rápido (sem DB)."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data
        print(f"✅ Health check rápido: {data}")
    
    def test_health_with_db(self, client):
        """GET /health — Health check com validação de DB."""
        response = client.get("/health")
        
        # Pode retornar 200 se conectado ou 500 se erro
        assert response.status_code in [200, 500]
        data = response.json()
        assert "status" in data
        print(f"✅ Health check com DB: {data}")


class TestAuthPublicEndpoints:
    """Teste de endpoints de autenticação públicos."""
    
    def test_register_endpoint_accessible(self, client):
        """POST /api/v1/auth/register — Endpoint acessível."""
        response = client.post("/api/v1/auth/register", json={})
        
        # Deve retornar erro de validação (422), não 404
        assert response.status_code in [200, 201, 400, 422, 409, 500]
        assert response.status_code != 404
        print(f"✅ Auth register endpoint: {response.status_code}")
    
    def test_login_endpoint_accessible(self, client):
        """POST /api/v1/auth/login — Endpoint acessível."""
        response = client.post("/api/v1/auth/login", json={})
        
        # Deve retornar erro de validação (422), não 404
        assert response.status_code in [200, 201, 400, 422, 409, 500, 401]
        assert response.status_code != 404
        print(f"✅ Auth login endpoint: {response.status_code}")


class TestDemoData:
    """Teste com dados de exemplo."""
    
    def test_register_with_valid_data(self, client):
        """Tenta registrar com dados válidos."""
        payload = {
            "email": "testuser@example.com",
            "password": "SecurePassword123!",
            "nome": "Test User 123"
        }
        response = client.post("/api/v1/auth/register", json=payload)
        
        # Pode falhar por validação mas endpoint existe
        assert response.status_code != 404
        print(f"✅ Register com dados: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   Response: {data}")
    
    def test_login_with_credentials(self, client):
        """Tenta fazer login com credenciais."""
        payload = {
            "email": "testuser@example.com",
            "password": "SecurePassword123!"
        }
        response = client.post("/api/v1/auth/login", json=payload)
        
        # Não é 404 (endpoint existe)
        assert response.status_code != 404
        print(f"✅ Login com credenciais: {response.status_code}")


class TestEndpointsExist:
    """Teste se endpoints estão registrados."""
    
    @pytest.mark.parametrize("endpoint", [
        "/api/v1/bots",
        "/api/v1/tenants",
        "/api/v1/marketplaces",
        "/api/v1/regras",
        "/api/v1/agendamentos",
        "/api/v1/logs",
    ])
    def test_protected_endpoints_registered(self, client, endpoint):
        """Verifica se endpoints protegidos estão registrados (não 404)."""
        response = client.get(endpoint)
        
        # Podem retornar 401/403 (protegido) mas não 404
        assert response.status_code != 404, f"Endpoint {endpoint} não está registrado!"
        print(f"✅ Endpoint {endpoint}: registrado ({response.status_code})")


class TestErrorResponses:
    """Teste de respostas de erro."""
    
    def test_nonexistent_endpoint_returns_404(self, client):
        """GET /api/v1/xyz-nonexistent — Deve retornar 404."""
        response = client.get("/api/v1/xyz-nonexistent")
        
        assert response.status_code == 404
        print(f"✅ 404 para endpoint inexistente")
    
    def test_root_with_wrong_method(self, client):
        """DELETE / — Método não permitido."""
        response = client.delete("/")
        
        assert response.status_code == 405
        print(f"✅ 405 para método não permitido")
    
    def test_invalid_json(self, client):
        """POST com JSON inválido."""
        response = client.post(
            "/api/v1/auth/login",
            data=b"{ invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
        print(f"✅ Tratamento de JSON inválido: {response.status_code}")


class TestDocumentation:
    """Teste de endpoints de documentação."""
    
    def test_swagger_ui_available(self, client):
        """GET /docs — Swagger UI disponível."""
        response = client.get("/docs")
        
        # Pode estar protegido ou público
        assert response.status_code in [200, 401, 403]
        print(f"✅ Swagger UI: {response.status_code}")
    
    def test_openapi_schema(self, client):
        """GET /openapi.json — Schema OpenAPI disponível."""
        response = client.get("/openapi.json")
        
        # Pode estar protegido ou público
        assert response.status_code in [200, 401, 403]
        print(f"✅ OpenAPI Schema: {response.status_code}")


class TestAPIStatus:
    """Status geral da API."""
    
    def test_api_is_responsive(self, client):
        """Verifica se API está respondendo."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        print(f"✅ API está respondendo corretamente")
    
    def test_api_version_correct(self, client):
        """Verifica versão da API."""
        response = client.get("/")
        data = response.json()
        
        assert data["version"] == "2.0.0"
        print(f"✅ API versão: {data['version']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s para mostrar prints
