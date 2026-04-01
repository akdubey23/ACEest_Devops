from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import Flask, jsonify


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
            "phase": 1,
            "version_source": "Aceestver-1.0.py",
            "endpoints": ["/health", "/programs", "/programs/<name>"],
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

