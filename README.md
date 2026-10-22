# AIOps Vision — AI Model Deployment & Monitoring Platform

A full-stack PS4 AI DevOps mini-project for third-year AI&DS students.

## Features
- Flask REST API and responsive HTML/CSS/JavaScript dashboard
- Iris species ML classifier using scikit-learn
- SQLite prediction history and operational events
- Model metadata and a 90% validation-accuracy quality gate
- Prediction distribution chart
- Model retraining endpoint
- pytest automated tests
- Docker packaging and Jenkins pipeline

## Run locally on Windows
1. Install Python 3.11 or 3.12 and Git. Install Docker Desktop and Jenkins later for the DevOps stages.
2. Open this folder in VS Code.
3. In the VS Code terminal:
   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python train_model.py
   python app.py
   ```
4. Open http://127.0.0.1:5000 in a browser.
5. In a second terminal, activate `.venv` and run `python -m pytest -q`.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## API endpoints
- `GET /api/health`
- `GET /api/model`
- `GET /api/metrics`
- `GET /api/predictions`
- `POST /api/predict`
- `POST /api/retrain`

Example prediction JSON:
```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

## Docker
```powershell
docker build -t aiops-vision:latest .
docker run --name aiops-vision-app -p 5000:5000 aiops-vision:latest
```
Then open http://127.0.0.1:5000.

## Jenkins
The included `Jenkinsfile` uses Windows `bat` steps. Configure a Jenkins Pipeline job pointing to this Git repository, and ensure the Jenkins agent has Python, Git, and Docker available. For a Linux agent, replace `bat` with `sh`.

## Important note
The dashboard's accuracy is the model's held-out test accuracy, not live production accuracy. The prediction history and distribution are based on requests made to this demo app.
