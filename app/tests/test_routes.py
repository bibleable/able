import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_route_without_multipart():
    response = client.post("/login", data={"username": "test", "password": "test"})
    assert response.status_code == 500
    assert "Form data requires 'python-multipart' to be installed." in response.text

def test_login_route_with_multipart_installed(monkeypatch):
    monkeypatch.setattr("app.dependencies.ensure_multipart_is_installed", lambda: None)
    response = client.post("/login", data={"username": "test", "password": "test"})
    assert response.status_code == 200
    assert "Login successful" in response.text  # Adjust based on actual success response

def test_search_endpoint(client):
    """Test the search endpoint returns successfully"""
    response = client.get("/search?q=John 3:16")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_verses_endpoint(client):
    """Test the verses endpoint returns successfully"""
    response = client.get("/verses?passage=John 3:16")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
def test_login_page(client):
    """Test the login page loads successfully"""
    response = client.get("/login")
    assert response.status_code == 200