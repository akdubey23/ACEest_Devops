import importlib
import os
import sys


def _make_client(tmp_path):
    """
    Through Phase 7 we rely on SQLite persistence.
    Each test uses its own temporary DB to avoid state bleed.
    """
    db_path = tmp_path / "test_aceest.db"
    os.environ["ACEEST_DB_PATH"] = str(db_path)

    # Ensure the module re-reads ACEEST_DB_PATH on import.
    sys.modules.pop("app", None)
    app_module = importlib.import_module("app")
    return app_module.app.test_client()


def _create_client(client, **overrides):
    payload = {
        "name": "Akanksha",
        "age": 25,
        "height_cm": 165.0,
        "weight_kg": 60.0,
        "program": "Fat Loss (FL)",
        "adherence": 80,
        "notes": "n",
        "target_weight_kg": 55.0,
        "target_adherence": 85,
    }
    payload.update(overrides)
    resp = client.post("/clients", json=payload)
    assert resp.status_code == 201
    return resp.get_json()["client"]


def test_health_ok(tmp_path):
    client = _make_client(tmp_path)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_programs_and_client_crud(tmp_path):
    client = _make_client(tmp_path)

    resp = client.get("/programs")
    assert resp.status_code == 200
    assert any(p["name"] == "Fat Loss (FL)" for p in resp.get_json()["programs"])

    created = _create_client(client, name="A")
    assert created["name"] == "A"
    assert created["estimated_calories"] == int(60.0 * 22)

    fetched = client.get("/clients/A").get_json()["client"]
    assert fetched["name"] == "A"
    assert fetched["height_cm"] == 165.0
    assert fetched["target_adherence"] == 85


def test_csv_and_adherence_analytics(tmp_path):
    client = _make_client(tmp_path)
    _create_client(client, name="A", adherence=40, program="Beginner (BG)", weight_kg=50.0)
    _create_client(client, name="B", adherence=90, program="Muscle Gain (MG)", weight_kg=70.0)

    csv_resp = client.get("/clients/export.csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers.get("Content-Type", "")
    body = csv_resp.get_data(as_text=True)
    assert "Name,Age,Weight,Program,Adherence,Notes" in body

    a_resp = client.get("/analytics/adherence")
    assert a_resp.status_code == 200
    data = a_resp.get_json()
    assert set(data["labels"]) == {"A", "B"}
    assert set(data["values"]) == {40, 90}


def test_adherence_series_endpoint(tmp_path):
    client = _make_client(tmp_path)
    _create_client(client, name="A", adherence=10)
    _create_client(client, name="A", adherence=20)

    resp = client.get("/analytics/adherence/A")
    assert resp.status_code == 200
    series = resp.get_json()["series"]
    assert len(series) >= 2
    assert {p["adherence"] for p in series[-2:]} == {10, 20}


def test_workouts_and_metrics_and_bmi(tmp_path):
    client = _make_client(tmp_path)
    _create_client(client, name="A", height_cm=170.0, weight_kg=68.0)

    w_resp = client.post(
        "/workouts",
        json={
            "client_name": "A",
            "date": "2026-04-01",
            "workout_type": "Strength",
            "duration_min": 60,
            "notes": "session",
            "exercises": [{"name": "Squat", "sets": 3, "reps": 5, "weight": 80}],
        },
    )
    assert w_resp.status_code == 201

    list_resp = client.get("/workouts?client_name=A")
    assert list_resp.status_code == 200
    workouts = list_resp.get_json()["workouts"]
    assert len(workouts) >= 1
    assert workouts[0]["workout_type"] == "Strength"

    m1 = client.post("/metrics", json={"client_name": "A", "date": "2026-04-01", "weight": 68.0, "waist": 80.0, "bodyfat": 20.0})
    m2 = client.post("/metrics", json={"client_name": "A", "date": "2026-04-02", "weight": 67.5, "waist": 79.5, "bodyfat": 19.8})
    assert m1.status_code == 201 and m2.status_code == 201

    wt = client.get("/analytics/weight-trend?client_name=A")
    assert wt.status_code == 200
    series = wt.get_json()["series"]
    assert [p["date"] for p in series] == ["2026-04-01", "2026-04-02"]

    bmi_resp = client.get("/bmi?client_name=A")
    assert bmi_resp.status_code == 200
    data = bmi_resp.get_json()
    assert "bmi" in data and "category" in data and "risk" in data

