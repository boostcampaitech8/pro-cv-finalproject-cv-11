from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
import app.api.routes.connect as connect


# Fixture-free minimal patching so tests stay simple and self-contained
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
connect.SessionLocal = TestingSessionLocal  # patch to avoid external DB dependency

client = TestClient(app)


def test_connect_check():
    response = client.get("/api/v1/connect_check")
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "ok"


def test_db_check():
    response = client.get("/api/v1/db_check")
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "ok"
