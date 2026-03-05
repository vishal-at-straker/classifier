"""Rate limit: assert 429 after N requests within window."""
import pytest
from fastapi.testclient import TestClient

from src import main as main_module
from src.config import get_settings
from src.db.session import init_db
from src.main import app


@pytest.fixture
def client():
    init_db()
    if not getattr(app.state, "settings", None):
        app.state.settings = get_settings()
    return TestClient(app)


def test_rate_limit_returns_429_after_exceeding(client):
    # Ensure app has settings (TestClient may not run startup)
    if not getattr(app.state, "settings", None):
        app.state.settings = get_settings()
    # Clear rate limit state and use a low limit so we need only 3 requests
    main_module._rate_limit.clear()
    orig_limit = app.state.settings.rate_limit_requests
    app.state.settings.rate_limit_requests = 2
    try:
        for i in range(3):
            r = client.post(
                "/submissions",
                json={"text": f"Rate limit test {i}."},
            )
            if i < 2:
                assert r.status_code in (200, 201), (i, r.json())
            else:
                assert r.status_code == 429, (r.status_code, r.json())
    finally:
        app.state.settings.rate_limit_requests = orig_limit
