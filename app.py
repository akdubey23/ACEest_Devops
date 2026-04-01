from __future__ import annotations

import csv
import io
import os
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from flask import Flask, jsonify, request, Response


app = Flask(__name__)


# -------------------------
# Phase 1 (Aceestver-1.0.py)
# -------------------------
# Baseline program catalog: workout + diet plan per program.

PROGRAMS: dict[str, dict[str, Any]] = {
    "Fat Loss (FL)": {
        "workout": (
            "Mon: 5x5 Back Squat + AMRAP\n"
            "Tue: EMOM 20min Assault Bike\n"
            "Wed: Bench Press + 21-15-9\n"
            "Thu: 10RFT Deadlifts/Box Jumps\n"
            "Fri: 30min Active Recovery"
        ),
        "diet": (
            "B: 3 Egg Whites + Oats Idli\n"
            "L: Grilled Chicken + Brown Rice\n"
            "D: Fish Curry + Millet Roti\n"
            "Target: 2,000 kcal"
        ),
        "color": "#e74c3c",
    },
    "Muscle Gain (MG)": {
        "workout": (
            "Mon: Squat 5x5\n"
            "Tue: Bench 5x5\n"
            "Wed: Deadlift 4x6\n"
            "Thu: Front Squat 4x8\n"
            "Fri: Incline Press 4x10\n"
            "Sat: Barbell Rows 4x10"
        ),
        "diet": (
            "B: 4 Eggs + PB Oats\n"
            "L: Chicken Biryani (250g Chicken)\n"
            "D: Mutton Curry + Jeera Rice\n"
            "Target: 3,200 kcal"
        ),
        "color": "#2ecc71",
    },
    "Beginner (BG)": {
        "workout": (
            "Circuit Training: Air Squats, Ring Rows, Push-ups.\n"
            "Focus: Technique Mastery & Form (90% Threshold)"
        ),
        "diet": (
            "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\n"
            "Protein: 120g/day"
        ),
        "color": "#3498db",
    },
}


# -------------------------
# Phase 2 (Aceestver1.1.2.py)
# -------------------------
# In-memory client capture + CSV export + adherence chart data.
# Calorie factors are internal-only and used to return estimated_calories in client responses.

PROGRAM_CALORIE_FACTOR: dict[str, int] = {
    "Fat Loss (FL)": 22,
    "Muscle Gain (MG)": 35,
    "Beginner (BG)": 26,
}

# -------------------------
# Phase 4 (Aceestver2.0.1.py)
# -------------------------
# Replace in-memory client store with SQLite persistence.

DB_PATH = os.environ.get("ACEEST_DB_PATH", "aceest_fitness.db")


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _db() as conn:
        # Phase 4 schema (Aceestver2.0.1.py-inspired), with assignment constraints:
        # - Do not store calories (derived field only)
        # - Do not enforce UNIQUE on name (id is the primary key)
        #
        # If an older schema exists (e.g. had calories/UNIQUE), recreate the table.
        exists = (
            conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='clients'")
            .fetchone()
            is not None
        )
        if exists:
            cols = [r["name"] for r in conn.execute("PRAGMA table_info(clients)").fetchall()]
            required = {
                "id",
                "name",
                "age",
                "height_cm",
                "weight",
                "program",
                "adherence",
                "notes",
                "target_weight_kg",
                "target_adherence",
            }
            # If schema differs (e.g. contains calories), drop and recreate.
            if set(cols) != required:
                conn.execute("DROP TABLE clients")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                height_cm REAL,
                weight REAL,
                program TEXT,
                adherence INTEGER,
                notes TEXT,
                target_weight_kg REAL,
                target_adherence INTEGER
            )
            """
        )

        # Phase 6 (Aceestver-2.2.1.py): progress table for charting
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT,
                week TEXT,
                adherence INTEGER
            )
            """
        )

        # Phase 7 (Aceestver-2.2.4.py): workouts, exercises, and metrics tables
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT,
                date TEXT,
                workout_type TEXT,
                duration_min INTEGER,
                notes TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER,
                name TEXT,
                sets INTEGER,
                reps INTEGER,
                weight REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT,
                date TEXT,
                weight REAL,
                waist REAL,
                bodyfat REAL
            )
            """
        )


init_db()


@dataclass
class Client:
    name: str
    age: int = 0
    height_cm: float = 0.0
    weight_kg: float = 0.0
    program: str = ""
    adherence: int = 0
    notes: str = ""
    target_weight_kg: float = 0.0
    target_adherence: int = 0

    def to_dict(self) -> dict[str, Any]:
        estimated_calories = None
        if self.weight_kg > 0 and self.program in PROGRAM_CALORIE_FACTOR:
            estimated_calories = int(self.weight_kg * PROGRAM_CALORIE_FACTOR[self.program])
        return {
            "name": self.name,
            "age": self.age,
            "weight_kg": self.weight_kg,
            "program": self.program,
            "adherence": self.adherence,
            "notes": self.notes,
            "estimated_calories": estimated_calories,
        }


@dataclass(frozen=True)
class ApiError(Exception):
    status_code: int
    message: str


@app.errorhandler(ApiError)
def handle_api_error(err: ApiError):
    return jsonify({"error": err.message}), err.status_code


@app.get("/")
def home():
    return jsonify(
        {
            "service": "ACEest Fitness & Gym API",
            "phase": 4,
            "version_source": "Aceestver2.0.1.py",
            "endpoints": [
                "/health",
                "/programs",
                "/programs/<name>",
                "/clients",
                "/clients/<name>",
                "/clients/export.csv",
                "/analytics/adherence",
            ],
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/programs")
def list_programs():
    return jsonify({"programs": [{"name": name, **data} for name, data in PROGRAMS.items()]})


@app.get("/programs/<string:name>")
def get_program(name: str):
    if name not in PROGRAMS:
        raise ApiError(404, f"Program not found: {name}")
    return jsonify({"name": name, **PROGRAMS[name]})


@app.get("/clients")
def list_clients():
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, name, age, height_cm, weight, program, adherence, notes, "
            "target_weight_kg, target_adherence "
            "FROM clients ORDER BY name, id"
        ).fetchall()
    clients: list[dict[str, Any]] = []
    for r in rows:
        program = r["program"] or ""
        weight_kg = float(r["weight"] or 0.0)
        estimated_calories = None
        if weight_kg > 0 and program in PROGRAM_CALORIE_FACTOR:
            estimated_calories = int(weight_kg * PROGRAM_CALORIE_FACTOR[program])
        clients.append(
            {
                "name": r["name"],
                "age": r["age"] or 0,
                "height_cm": float(r["height_cm"] or 0.0),
                "weight_kg": weight_kg,
                "program": program,
                "adherence": int(r["adherence"] or 0),
                "notes": r["notes"] or "",
                "estimated_calories": estimated_calories,
                "target_weight_kg": float(r["target_weight_kg"] or 0.0),
                "target_adherence": int(r["target_adherence"] or 0),
            }
        )
    return jsonify({"clients": clients})


@app.post("/clients")
def save_client():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name") or "").strip()
    program = str(payload.get("program") or "").strip()
    if not name or not program:
        raise ApiError(400, "Fields 'name' and 'program' are required")
    if program not in PROGRAMS:
        raise ApiError(400, f"Unknown program: {program}")

    age = int(payload.get("age") or 0)
    height_cm = float(payload.get("height_cm") or 0.0)
    weight_kg = float(payload.get("weight_kg") or 0.0)
    adherence = int(payload.get("adherence") or 0)
    notes = str(payload.get("notes") or "")
    target_weight_kg = float(payload.get("target_weight_kg") or 0.0)
    target_adherence = int(payload.get("target_adherence") or 0)

    with _db() as conn:
        conn.execute(
            """
            INSERT INTO clients (
              name, age, height_cm, weight, program, adherence, notes, target_weight_kg, target_adherence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, age, height_cm, weight_kg, program, adherence, notes, target_weight_kg, target_adherence),
        )

        # Phase 6 support: capture adherence into progress history for charting
        week = datetime.now().strftime("Week %U - %Y")
        conn.execute(
            "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
            (name, week, adherence),
        )

    client = Client(
        name=name,
        age=age,
        height_cm=height_cm,
        weight_kg=weight_kg,
        program=program,
        adherence=adherence,
        notes=notes,
        target_weight_kg=target_weight_kg,
        target_adherence=target_adherence,
    )
    return jsonify({"client": client.to_dict()}), 201


@app.get("/clients/<string:name>")
def get_client(name: str):
    with _db() as conn:
        r = conn.execute(
            "SELECT id, name, age, height_cm, weight, program, adherence, notes, target_weight_kg, target_adherence "
            "FROM clients WHERE name=? ORDER BY id DESC LIMIT 1",
            (name,),
        ).fetchone()
    if not r:
        raise ApiError(404, f"Client not found: {name}")
    program = r["program"] or ""
    weight_kg = float(r["weight"] or 0.0)
    estimated_calories = None
    if weight_kg > 0 and program in PROGRAM_CALORIE_FACTOR:
        estimated_calories = int(weight_kg * PROGRAM_CALORIE_FACTOR[program])
    return jsonify(
        {
            "client": {
                "name": r["name"],
                "age": r["age"] or 0,
                "height_cm": float(r["height_cm"] or 0.0),
                "weight_kg": weight_kg,
                "program": program,
                "adherence": int(r["adherence"] or 0),
                "notes": r["notes"] or "",
                "estimated_calories": estimated_calories,
                "target_weight_kg": float(r["target_weight_kg"] or 0.0),
                "target_adherence": int(r["target_adherence"] or 0),
            }
        }
    )


@app.get("/clients/export.csv")
def export_clients_csv():
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Name", "Age", "Weight", "Program", "Adherence", "Notes"])
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, name, age, weight, program, adherence, notes FROM clients ORDER BY name, id"
        ).fetchall()
    for r in rows:
        writer.writerow(
            [
                r["name"],
                r["age"] or 0,
                float(r["weight"] or 0.0),
                r["program"] or "",
                int(r["adherence"] or 0),
                r["notes"] or "",
            ]
        )
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=clients.csv"},
    )


@app.get("/analytics/adherence")
def adherence_chart_data():
    with _db() as conn:
        rows = conn.execute("SELECT name, adherence FROM clients ORDER BY name").fetchall()
    return jsonify({"labels": [r["name"] for r in rows], "values": [int(r["adherence"] or 0) for r in rows]})


# -------------------------
# Phase 6 (Aceestver-2.2.1.py)
# -------------------------


@app.get("/analytics/adherence/<string:client_name>")
def adherence_series(client_name: str):
    with _db() as conn:
        rows = conn.execute(
            "SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id",
            (client_name,),
        ).fetchall()
    return jsonify(
        {
            "client": client_name,
            "series": [{"week": r["week"], "adherence": int(r["adherence"] or 0)} for r in rows],
        }
    )


# -------------------------
# Phase 7 (Aceestver-2.2.4.py)
# -------------------------


@app.post("/workouts")
def create_workout():
    payload = request.get_json(silent=True) or {}
    client_name = str(payload.get("client_name") or "").strip()
    if not client_name:
        raise ApiError(400, "Field 'client_name' is required")

    workout_date = str(payload.get("date") or date.today().isoformat())
    workout_type = str(payload.get("workout_type") or "").strip()
    if not workout_type:
        raise ApiError(400, "Field 'workout_type' is required")

    duration_min = int(payload.get("duration_min") or 0)
    notes = str(payload.get("notes") or "")
    exercises = payload.get("exercises") or []

    with _db() as conn:
        cur = conn.execute(
            "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?,?,?,?,?)",
            (client_name, workout_date, workout_type, duration_min, notes),
        )
        workout_id = cur.lastrowid

        for ex in exercises:
            ex_name = str(ex.get("name") or "").strip()
            if not ex_name:
                continue
            conn.execute(
                "INSERT INTO exercises (workout_id, name, sets, reps, weight) VALUES (?,?,?,?,?)",
                (
                    workout_id,
                    ex_name,
                    int(ex.get("sets") or 0),
                    int(ex.get("reps") or 0),
                    float(ex.get("weight") or 0.0),
                ),
            )

    return jsonify({"workout_id": workout_id}), 201


@app.get("/workouts")
def list_workouts():
    client_name = str(request.args.get("client_name") or "").strip()
    if not client_name:
        raise ApiError(400, "Query param 'client_name' is required")

    with _db() as conn:
        rows = conn.execute(
            "SELECT id, date, workout_type, duration_min, notes "
            "FROM workouts WHERE client_name=? ORDER BY date DESC, id DESC",
            (client_name,),
        ).fetchall()

    return jsonify(
        {
            "client": client_name,
            "workouts": [
                {
                    "id": r["id"],
                    "date": r["date"],
                    "workout_type": r["workout_type"],
                    "duration_min": int(r["duration_min"] or 0),
                    "notes": r["notes"] or "",
                }
                for r in rows
            ],
        }
    )


@app.post("/metrics")
def create_metrics():
    payload = request.get_json(silent=True) or {}
    client_name = str(payload.get("client_name") or "").strip()
    if not client_name:
        raise ApiError(400, "Field 'client_name' is required")

    metrics_date = str(payload.get("date") or date.today().isoformat())
    weight = payload.get("weight")
    waist = payload.get("waist")
    bodyfat = payload.get("bodyfat")

    with _db() as conn:
        conn.execute(
            "INSERT INTO metrics (client_name, date, weight, waist, bodyfat) VALUES (?,?,?,?,?)",
            (client_name, metrics_date, weight, waist, bodyfat),
        )

    return jsonify({"status": "saved"}), 201


@app.get("/analytics/weight-trend")
def weight_trend():
    client_name = str(request.args.get("client_name") or "").strip()
    if not client_name:
        raise ApiError(400, "Query param 'client_name' is required")

    with _db() as conn:
        rows = conn.execute(
            "SELECT date, weight FROM metrics WHERE client_name=? AND weight IS NOT NULL ORDER BY date",
            (client_name,),
        ).fetchall()

    return jsonify({"client": client_name, "series": [{"date": r["date"], "weight": r["weight"]} for r in rows]})


@app.get("/bmi")
def bmi_info():
    client_name = str(request.args.get("client_name") or "").strip()
    if not client_name:
        raise ApiError(400, "Query param 'client_name' is required")

    with _db() as conn:
        r = conn.execute(
            "SELECT height_cm, weight FROM clients WHERE name=? ORDER BY id DESC LIMIT 1",
            (client_name,),
        ).fetchone()
    if not r:
        raise ApiError(404, f"Client not found: {client_name}")

    height_cm = float(r["height_cm"] or 0.0)
    weight_kg = float(r["weight"] or 0.0)
    if height_cm <= 0 or weight_kg <= 0:
        raise ApiError(400, "Client must have valid height_cm and weight_kg to compute BMI")

    h_m = height_cm / 100.0
    bmi = round(weight_kg / (h_m * h_m), 1)

    if bmi < 18.5:
        category = "Underweight"
        risk = "Potential nutrient deficiency, low energy."
    elif bmi < 25:
        category = "Normal"
        risk = "Low risk if active and strong."
    elif bmi < 30:
        category = "Overweight"
        risk = "Moderate risk; focus on adherence and progressive activity."
    else:
        category = "Obese"
        risk = "Higher risk; prioritize fat loss, consistency, and supervision."

    return jsonify({"client": client_name, "bmi": bmi, "category": category, "risk": risk})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

