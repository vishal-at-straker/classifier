"""GET /submissions/list: paginated list in descending order."""
import pytest
from fastapi.testclient import TestClient

from src.db.session import init_db
from src.main import app


@pytest.fixture
def client():
    init_db()
    return TestClient(app)


def test_list_submissions_empty(client):
    r = client.get("/submissions/list?page=1&per_page=10")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert data["page"] == 1
    assert data["per_page"] == 10
    assert isinstance(data["items"], list)


def test_list_submissions_pagination_params(client):
    r = client.get("/submissions/list?page=2&per_page=5")
    assert r.status_code == 200
    data = r.json()
    assert data["page"] == 2
    assert data["per_page"] == 5
