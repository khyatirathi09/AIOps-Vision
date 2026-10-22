from pathlib import Path
import json
from datetime import datetime, timezone

import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "iris_model.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

def train_and_save():
    dataset = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        dataset.data, dataset.target, test_size=0.2, random_state=42, stratify=dataset.target
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, random_state=42))
    model.fit(X_train, y_train)
    accuracy = float(accuracy_score(y_test, model.predict(X_test)))

    # Quality gate: fail the build if validation accuracy is below 90%.
    if accuracy < 0.90:
        raise RuntimeError(f"Model quality gate failed: accuracy={accuracy:.3f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    metadata = {
        "name": "Iris Species Classifier",
        "version": "v1.0",
        "algorithm": "StandardScaler + Logistic Regression",
        "dataset": "Iris dataset (150 samples, 4 numeric features)",
        "accuracy": round(accuracy, 4),
        "quality_gate": "PASS" if accuracy >= 0.90 else "FAIL",
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "classes": dataset.target_names.tolist(),
        "features": ["Sepal length", "Sepal width", "Petal length", "Petal width"]
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata

if __name__ == "__main__":
    result = train_and_save()
    print(json.dumps(result, indent=2))
