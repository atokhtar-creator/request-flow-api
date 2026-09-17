import importlib
import os


def load_client(tmp_path):
    os.environ["REQUEST_FLOW_DB"] = str(tmp_path / "test.db")
    import app.main
    importlib.reload(app.main)

    from fastapi.testclient import TestClient
    return TestClient(app.main.app)


def test_request_lifecycle(tmp_path):
    client = load_client(tmp_path)
    created = client.post(
        "/requests",
        json={"title": "Cannot access LMS", "description": "Login fails after password change"},
    )
    assert created.status_code == 201
    request_id = created.json()["id"]
    assert created.json()["status"] == "NEW"

    progress = client.patch(f"/requests/{request_id}/status", json={"status": "IN_PROGRESS"})
    assert progress.status_code == 200
    assert progress.json()["status"] == "IN_PROGRESS"

    history = client.get(f"/requests/{request_id}/history")
    assert history.status_code == 200
    assert len(history.json()) == 2


def test_invalid_transition_returns_409(tmp_path):
    client = load_client(tmp_path)
    created = client.post("/requests", json={"title": "Test ticket", "description": "Something happened"})
    request_id = created.json()["id"]
    response = client.patch(f"/requests/{request_id}/status", json={"status": "CLOSED"})
    assert response.status_code == 409
