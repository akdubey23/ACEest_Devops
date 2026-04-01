from app import app


def test_health_ok():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_list_programs():
    client = app.test_client()
    resp = client.get("/programs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "programs" in data
    assert any(p["name"] == "Fat Loss (FL)" for p in data["programs"])


def test_create_client_and_fetch():
    client = app.test_client()
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

