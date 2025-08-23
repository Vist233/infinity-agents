import pytest
from app.app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_chat_route(client):
    response = client.get('/chat')
    assert response.status_code == 200

def test_trait_recognizer_route(client):
    response = client.get('/trait_recognizer')
    assert response.status_code == 200