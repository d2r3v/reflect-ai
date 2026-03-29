"""Tests for health check routes."""
import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


def test_health_check_returns_200(client: TestClient):
    """Test that health check endpoint returns 200 OK."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_check_response_structure(client: TestClient):
    """Test that health check response has required fields."""
    response = client.get("/api/v1/health")
    data = response.json()
    
    assert "status" in data
    assert "version" in data
    assert data["status"] == "healthy"


def test_health_check_version_not_empty(client: TestClient):
    """Test that version field is populated."""
    response = client.get("/api/v1/health")
    data = response.json()
    
    assert data["version"]
    assert isinstance(data["version"], str)
