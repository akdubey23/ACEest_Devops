from __future__ import annotations

import csv
import io
import os
import sqlite3
from dataclasses import dataclass
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
            required = {"id", "name", "age", "weight", "program", "adherence", "notes"}
            # If schema differs (e.g. contains calories), drop and recreate.
            if set(cols) != required:
                conn.execute("DROP TABLE clients")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                weight REAL,
                program TEXT,
                adherence INTEGER,
                notes TEXT
            )
            """
        )


init_db()


@dataclass
class Client:
    name: str
    age: int = 0
    weight_kg: float = 0.0
    program: str = ""
    adherence: int = 0
    notes: str = ""

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
            "SELECT id, name, age, weight, program, adherence, notes FROM clients ORDER BY name, id"
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
                "weight_kg": weight_kg,
                "program": program,
                "adherence": int(r["adherence"] or 0),
                "notes": r["notes"] or "",
                "estimated_calories": estimated_calories,
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
    weight_kg = float(payload.get("weight_kg") or 0.0)
    adherence = int(payload.get("adherence") or 0)
    notes = str(payload.get("notes") or "")

    with _db() as conn:
        conn.execute(
            """
            INSERT INTO clients (name, age, weight, program, adherence, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, age, weight_kg, program, adherence, notes),
        )

    client = Client(name=name, age=age, weight_kg=weight_kg, program=program, adherence=adherence, notes=notes)
    return jsonify({"client": client.to_dict()}), 201


@app.get("/clients/<string:name>")
def get_client(name: str):
    with _db() as conn:
        r = conn.execute(
            "SELECT id, name, age, weight, program, adherence, notes "
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
                "weight_kg": weight_kg,
                "program": program,
                "adherence": int(r["adherence"] or 0),
                "notes": r["notes"] or "",
                "estimated_calories": estimated_calories,
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

