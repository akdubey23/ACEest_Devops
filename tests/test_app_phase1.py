import importlib
import os
import sys


def _make_client(tmp_path):
    db_path = tmp_path / "test_aceest.db"
    os.environ["ACEEST_DB_PATH"] = str(db_path)

    # Ensure the module re-reads ACEEST_DB_PATH on import.
    sys.modules.pop("app", None)
    app_module = importlib.import_module("app")
    return app_module.app.test_client()


def test_health_ok(tmp_path):
    client = _make_client(tmp_path)
    # If PYTEST_TMPDIR isn't set, pytest will still provide tmp_path in other tests.
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_list_programs(tmp_path):
    client = _make_client(tmp_path)
    resp = client.get("/programs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "programs" in data
    assert any(p["name"] == "Fat Loss (FL)" for p in data["programs"])


def test_create_client_and_fetch(tmp_path):
    client = _make_client(tmp_path)
    resp = client.post(
        "/clients",
        json={"name": "Akanksha", "age": 25, "weight_kg": 60.0, "program": "Fat Loss (FL)", "adherence": 80},
    )
    assert resp.status_code == 201
    data = resp.get_json()["client"]
    assert data["name"] == "Akanksha"
    assert data["estimated_calories"] == int(60.0 * 22)

    resp2 = client.get("/clients/Akanksha")
    assert resp2.status_code == 200
    assert resp2.get_json()["client"]["name"] == "Akanksha"


def test_list_clients_csv_and_analytics(tmp_path):
    client = _make_client(tmp_path)

    client.post(
        "/clients",
        json={"name": "A", "age": 20, "weight_kg": 50.0, "program": "Beginner (BG)", "adherence": 40, "notes": "n1"},
    )
    client.post(
        "/clients",
        json={"name": "B", "age": 30, "weight_kg": 70.0, "program": "Muscle Gain (MG)", "adherence": 90, "notes": "n2"},
    )

    # List clients
    resp = client.get("/clients")
    assert resp.status_code == 200
    clients = resp.get_json()["clients"]
    assert {c["name"] for c in clients} == {"A", "B"}

    # CSV export
    csv_resp = client.get("/clients/export.csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers.get("Content-Type", "")
    body = csv_resp.get_data(as_text=True)
    assert "Name,Age,Weight,Program,Adherence,Notes" in body

    # Adherence analytics
    a_resp = client.get("/analytics/adherence")
    assert a_resp.status_code == 200
    data = a_resp.get_json()
    assert set(data["labels"]) == {"A", "B"}
    assert set(data["values"]) == {40, 90}

