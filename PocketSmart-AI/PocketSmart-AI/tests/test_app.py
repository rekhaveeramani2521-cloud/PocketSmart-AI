import os
os.environ["AI_ENABLED"] = "false"
os.environ["DATABASE_URL"] = "sqlite:///./test_pocketsmart.db"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient
from main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_register_and_generate_home():
    with TestClient(app) as client:
        response = client.post(
            "/register",
            data={"name": "Test User", "email": "test@example.com", "password": "password123"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "Hello, Test User" in response.text

        response = client.post(
            "/generate-home",
            data={"budget": "20000", "rooms": "Living room", "style": "Modern", "needs": "lights, curtains, storage"},
        )
        assert response.status_code == 200
        assert "Home Interior Budget Plan" in response.text
        assert "Estimated total" in response.text


def test_token_invalid_credentials():
    with TestClient(app) as client:
        response = client.post("/token", data={"email": "missing@example.com", "password": "badpass123"})
        assert response.status_code == 401
