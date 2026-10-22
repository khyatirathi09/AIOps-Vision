from pathlib import Path
import json
import sqlite3
from datetime import datetime, timezone

import joblib
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from train_model import train_and_save, MODEL_PATH, METADATA_PATH

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "aiops.db"
FRONTEND_PATH = ROOT / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_PATH), static_url_path="")
CORS(app)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                sepal_length REAL NOT NULL,
                sepal_width REAL NOT NULL,
                petal_length REAL NOT NULL,
                petal_width REAL NOT NULL,
                prediction TEXT NOT NULL,
                model_version TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS model_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

def load_model():
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        train_and_save()
    return joblib.load(MODEL_PATH)

def read_metadata():
    if not METADATA_PATH.exists():
        train_and_save()
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))

def record_event(event_type, message, status="success"):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO model_events(created_at,event_type,message,status) VALUES(?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"), event_type, message, status)
        )

init_db()
model = load_model()
record_event("startup", "AI prediction service started", "success")

@app.get("/")
def home():
    return send_from_directory(FRONTEND_PATH, "index.html")

@app.get("/api/health")
def health():
    return jsonify({"status": "healthy", "service": "AIOps Vision API"})

@app.get("/api/model")
def model_info():
    metadata = read_metadata()
    return jsonify(metadata)

@app.get("/api/metrics")
def metrics():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) AS n FROM predictions").fetchone()["n"]
        recent = conn.execute(
            "SELECT prediction, COUNT(*) AS n FROM predictions GROUP BY prediction"
        ).fetchall()
        events = conn.execute("SELECT COUNT(*) AS n FROM model_events").fetchone()["n"]
        latest = conn.execute(
            "SELECT created_at, prediction FROM predictions ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return jsonify({
        "total_predictions": total,
        "model_accuracy": read_metadata().get("accuracy", 0),
        "model_version": read_metadata().get("version", "v1.0"),
        "service_status": "Healthy",
        "model_events": events,
        "prediction_breakdown": [{"label": row["prediction"], "count": row["n"]} for row in recent],
        "latest_prediction": dict(latest) if latest else None
    })

@app.get("/api/predictions")
def prediction_history():
    limit = min(max(request.args.get("limit", default=10, type=int), 1), 100)
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return jsonify([dict(row) for row in rows])

@app.post("/api/predict")
def predict():
    global model
    data = request.get_json(silent=True) or {}
    fields = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
    try:
        values = [float(data[field]) for field in fields]
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Provide numeric sepal_length, sepal_width, petal_length, and petal_width values."}), 400

    if any(value <= 0 or value > 10 for value in values):
        return jsonify({"error": "Each measurement must be greater than 0 and no more than 10 cm."}), 400

    metadata = read_metadata()
    prediction_index = int(model.predict([values])[0])
    prediction = metadata.get("classes", ["setosa", "versicolor", "virginica"])[prediction_index]
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_db() as conn:
        conn.execute("""
            INSERT INTO predictions(
                created_at,sepal_length,sepal_width,petal_length,petal_width,prediction,model_version
            ) VALUES(?,?,?,?,?,?,?)
        """, (created_at, *values, prediction, metadata.get("version", "v1.0")))
    record_event("prediction", f"Prediction generated: {prediction}", "success")
    return jsonify({
        "prediction": prediction,
        "model_version": metadata.get("version", "v1.0"),
        "created_at": created_at
    })

@app.post("/api/retrain")
def retrain():
    global model
    metadata = train_and_save()
    model = joblib.load(MODEL_PATH)
    record_event("retrain", f"Model retrained; validation accuracy {metadata['accuracy']:.3f}", "success")
    return jsonify({"message": "Model retrained and quality gate passed.", "model": metadata})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
