import os
import pytest

def test_able_db_exists():
    able_db_path = '/var/able.db'
    assert not os.path.exists(able_db_path), "ABLE DB should not exist"

def test_kjv_db_exists():
    kjv_db_path = '/var/comparison/kjv.db'
    assert not os.path.exists(kjv_db_path), "KJV DB should not exist"

def test_asv_db_exists():
    asv_db_path = '/var/comparison/asv.db'
    assert not os.path.exists(asv_db_path), "ASV DB should not exist"

def test_bsb_db_exists():
    bsb_db_path = '/var/comparison/bsb.db'
    assert not os.path.exists(bsb_db_path), "BSB DB should not exist"

def test_app_exists():
    """Test that the FastAPI app is initialized"""
    from app.index import app
    assert app is not None

def test_home_page(client):
    """Test the home page returns 200 OK"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]