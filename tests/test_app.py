import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from app import app

def test_health_endpoint():
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"

def test_model_metadata_has_quality_gate():
    client = app.test_client()
    response = client.get("/api/model")
    assert response.status_code == 200
    data = response.get_json()
    assert data["accuracy"] >= 0.90
    assert data["quality_gate"] == "PASS"

def test_prediction_requires_numeric_inputs():
    client = app.test_client()
    response = client.post("/api/predict", json={"sepal_length": "wrong"})
    assert response.status_code == 400

def test_prediction_saves_record():
    client = app.test_client()
    response = client.post("/api/predict", json={
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    })
    assert response.status_code == 200
    assert response.get_json()["prediction"] in ["setosa", "versicolor", "virginica"]
