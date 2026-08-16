from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db

client = TestClient(app)


def test_discovery_run_api(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        payload = {
            "city": "Ahmedabad",
            "keywords": ["cafe"],
            "limit_per_keyword": 2
        }
        res = client.post("/api/v1/discovery/run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "metrics" in data
        assert data["metrics"]["new_leads_count"] > 0
    finally:
        app.dependency_overrides.clear()
