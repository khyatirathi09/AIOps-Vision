let distributionChart;

async function api(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || data.message || "Request failed");
  return data;
}

function prettyDate(value) {
  if (!value) return "--";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

async function loadHealth() {
  try {
    await api("/api/health");
    document.getElementById("sidebar-status").textContent = "Operational";
    document.getElementById("health-value").textContent = "Healthy";
  } catch {
    document.getElementById("sidebar-status").textContent = "Unavailable";
    document.getElementById("health-value").textContent = "Offline";
  }
}

async function loadModel() {
  const model = await api("/api/model");
  document.getElementById("model-version").textContent = model.version;
  document.getElementById("model-name").textContent = model.name;
  document.getElementById("model-algorithm").textContent = model.algorithm;
  document.getElementById("algorithm").textContent = model.algorithm;
  document.getElementById("dataset").textContent = model.dataset;
  document.getElementById("accuracy").textContent = `${(model.accuracy * 100).toFixed(1)}%`;
  document.getElementById("trained-at").textContent = prettyDate(model.trained_at);
  document.getElementById("quality-gate").textContent = `QUALITY ${model.quality_gate}`;
  document.getElementById("quality-gate").className = model.quality_gate === "PASS" ? "pass-badge" : "pass-badge fail";
}

async function loadMetrics() {
  const metrics = await api("/api/metrics");
  document.getElementById("total-predictions").textContent = metrics.total_predictions;
  const labels = ["setosa", "versicolor", "virginica"];
  const counts = labels.map(label => {
    const found = metrics.prediction_breakdown.find(item => item.label === label);
    return found ? found.count : 0;
  });
  document.getElementById("chart-empty").style.display = metrics.total_predictions ? "none" : "grid";
  const context = document.getElementById("distribution-chart");
  if (distributionChart) distributionChart.destroy();
  distributionChart = new Chart(context, {
    type: "doughnut",
    data: {
      labels: ["Setosa", "Versicolor", "Virginica"],
      datasets: [{ data: counts, backgroundColor: ["#795be9", "#25b8ad", "#f1b44c"], borderWidth: 0, hoverOffset: 5 }]
    },
    options: { responsive: true, maintainAspectRatio: false, cutout: "72%", plugins: { legend: { display: false } } }
  });
}

async function loadHistory() {
  const rows = await api("/api/predictions?limit=8");
  const body = document.getElementById("history-body");
  if (!rows.length) {
    body.innerHTML = '<tr><td colspan="5" class="empty-row">No predictions yet. Run your first prediction above.</td></tr>';
    return;
  }
  body.innerHTML = rows.map(row => `
    <tr>
      <td>${prettyDate(row.created_at)}</td>
      <td>${Number(row.sepal_length).toFixed(1)} × ${Number(row.sepal_width).toFixed(1)}</td>
      <td>${Number(row.petal_length).toFixed(1)} × ${Number(row.petal_width).toFixed(1)}</td>
      <td><span class="class-pill">${row.prediction}</span></td>
      <td>${row.model_version}</td>
    </tr>`).join("");
}

async function refreshDashboard() {
  try {
    await Promise.all([loadHealth(), loadModel(), loadMetrics(), loadHistory()]);
  } catch (error) {
    console.error(error);
    document.getElementById("sidebar-status").textContent = "API error";
  }
}

document.getElementById("prediction-form").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = document.getElementById("predict-btn");
  const result = document.getElementById("prediction-result");
  const values = Object.fromEntries(new FormData(form).entries());
  for (const key of Object.keys(values)) values[key] = Number(values[key]);
  button.disabled = true;
  button.textContent = "Running model…";
  result.classList.add("hidden");
  try {
    const data = await api("/api/predict", { method: "POST", body: JSON.stringify(values) });
    result.innerHTML = `<div><strong>${data.prediction}</strong><small>Prediction generated successfully · Model ${data.model_version}</small></div><span class="pass-badge">SUCCESS</span>`;
    result.classList.remove("hidden");
    await Promise.all([loadMetrics(), loadHistory()]);
  } catch (error) {
    result.innerHTML = `<div><strong style="color:#c04b5a">Prediction failed</strong><small>${error.message}</small></div>`;
    result.classList.remove("hidden");
  } finally {
    button.disabled = false;
    button.innerHTML = 'Generate prediction <span>→</span>';
  }
});

document.getElementById("retrain-btn").addEventListener("click", async () => {
  const button = document.getElementById("retrain-btn");
  const message = document.getElementById("retrain-message");
  button.disabled = true;
  button.textContent = "Retraining model…";
  message.textContent = "";
  try {
    const data = await api("/api/retrain", { method: "POST", body: "{}" });
    message.textContent = data.message;
    await refreshDashboard();
  } catch (error) {
    message.textContent = error.message;
    message.style.color = "#c04b5a";
  } finally {
    button.disabled = false;
    button.innerHTML = "⟳ &nbsp; Retrain & validate model";
  }
});

document.getElementById("refresh-btn").addEventListener("click", refreshDashboard);
refreshDashboard();
