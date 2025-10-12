import pytest
from fastapi.testclient import TestClient
from app.index import app

@pytest.fixture
def client():
    """Return a TestClient instance for testing FastAPI routes"""
    return TestClient(app)

from .conftest import *

def test_hello_world():
    assert True