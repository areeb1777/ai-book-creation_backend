"""
Integration Tests for API Endpoints

Tests actual API endpoints with FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test /api/health endpoint"""

    def test_health_endpoint_exists(self):
        """Test health endpoint is accessible"""
        response = client.get("/api/health")
        assert response.status_code in [200, 503]  # May be degraded without .env

    def test_health_response_structure(self):
        """Test health response has correct structure"""
        response = client.get("/api/health")
        data = response.json()

        assert "status" in data
        assert "services" in data
        assert "version" in data

        assert "qdrant" in data["services"]
        assert "neon" in data["services"]
        assert "openai" in data["services"]


class TestQueryEndpoint:
    """Test /api/query endpoint"""

    def test_query_endpoint_validation(self):
        """Test query validation rejects invalid input"""
        # Too short query
        response = client.post("/api/query", json={
            "query": "Hi"
        })
        assert response.status_code == 422  # Validation error

    def test_query_requires_minimum_length(self):
        """Test minimum query length requirement"""
        response = client.post("/api/query", json={
            "query": "Short"  # Less than 10 characters
        })
        assert response.status_code == 422

    def test_query_request_schema(self):
        """Test valid query request structure"""
        response = client.post("/api/query", json={
            "query": "What is Spec-Kit Plus and how do I use it?",
            "top_k": 5
        })

        # Will fail without proper .env, but should not be validation error
        assert response.status_code != 422


class TestSelectedTextEndpoint:
    """Test /api/query/selected endpoint"""

    def test_selected_text_validation(self):
        """Test selected text validation"""
        # Missing selected_text
        response = client.post("/api/query/selected", json={
            "query": "What does this mean?"
        })
        assert response.status_code == 422

    def test_selected_text_minimum_length(self):
        """Test selected text minimum length requirement"""
        response = client.post("/api/query/selected", json={
            "query": "What does this mean?",
            "selected_text": "Short"  # Less than 20 characters
        })
        assert response.status_code == 422


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "RAG Chatbot API"
        assert data["status"] == "running"
        assert "version" in data


class TestOpenAPIDocumentation:
    """Test API documentation endpoints"""

    def test_openapi_schema(self):
        """Test OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_swagger_docs(self):
        """Test Swagger UI is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_docs(self):
        """Test ReDoc UI is accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200
