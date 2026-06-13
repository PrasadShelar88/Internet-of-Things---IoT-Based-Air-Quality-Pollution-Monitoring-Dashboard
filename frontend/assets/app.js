const DEFAULT_BACKEND = "http://127.0.0.1:8000";
let backendUrl = localStorage.getItem("airQualityBackendUrl") || DEFAULT_BACKEND;
let aqiCanvas, envCanvas;

const $ = (id) => document.getElementById(id);

const demoRows = [
  { timestamp: new Date(Date.now() - 4 * 60000).toISOString(), aqi: 36, pm25: 15, pm10: 38, gas: 150, co2: 520, co: 1.4, temperature: 28, humidity: 53, pollution_status: "Good", alert_status: "NORMAL", message: "Demo data: backend is not connected yet." },
  { timestamp: new Date(Date.now() - 3 * 60000).toISOString(), aqi: 70, pm25: 35, pm10: 75, gas: 260, co2: 790, co: 4.1, temperature: 30, humidity: 57, pollution_status: "Moderate", alert_status: "NORMAL", message: "Demo data: start backend for live readings." },
  { timestamp: new Date(Date.now() - 2 * 60000).toISOString(), aqi: 130, pm25: 85, pm10: 140, gas: 420, co2: 1200, co: 9.8, temperature: 33, humidity: 61, pollution_status: "Poor", alert_status: "ALERT", message: "Demo alert: pollutant level high." },
  { timestamp: new Date(Date.now() - 1 * 60000).toISOString(), aqi: 225, pm25: 145, pm10: 270, gas: 690, co2: 1700, co: 17, temperature: 36, humidity: 68, pollution_status: "Hazardous", alert_status: "ALERT", message: "Demo alert: hazardous pollution level." }
];

function cleanUrl(url) {
  return String(url || DEFAULT_BACKEND).trim().replace(/\/+$/, "");
}

function api(path) {
  return `${cleanUrl(backendUrl)}${path}`;
}

async function apiJson(path, options = {}) {
  const response = await fetch(api(path), {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });
  if (!response.ok) {
    let detail = "";
    try { detail = JSON.stringify(await response.json()); } catch (_) { detail = await response.text(); }
    throw new Error(`HTTP ${response.status}: ${detail || response.statusText}`);
  }
  return response.json();
}

function number(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function formatNumber(value, digits = 1) {
  if (value === undefined || value === null || value === "") return "--";
  const n = Number(value);
  if (!Number.isFinite(n)) return String(value);
  return Math.abs(n) >= 100 ? String(Math.round(n)) : n.toFixed(digits);
}

function unwrapReading(payload) {
  if (!payload) return {};
  if (payload.reading) return payload.reading;
  if (payload.latest) return payload.latest;
  if (payload.data && !Array.isArray(payload.data)) return payload.data;
  return payload;
}

function unwrapRows(payload) {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.readings)) return payload.readings;
  if (Array.isArray(payload.data)) return payload.data;
  if (Array.isArray(payload.logs)) return payload.logs;
  if (payload.latest || payload.reading) return [unwrapReading(payload)];
  return [];
}

function getStatus(reading) {
  return reading.pollution_status || reading.category || reading.status || reading.pollution_level || classifyByAqi(reading.aqi);
}

function classifyByAqi(aqi) {
  const value = number(aqi, 0);
  if (value <= 50) return "Good";
  if (value <= 100) return "Moderate";
  if (value <= 200) return "Poor";
  return "Hazardous";
}

function statusClass(status) {
  const value = String(status || "").toLowerCase();
  if (value.includes("good")) return "good";
  if (value.includes("moderate")) return "moderate";
  if (value.includes("poor") || value.includes("unhealthy")) return "poor";
  if (value.includes("hazard")) return "hazardous";
  return "normal";
}

function isAlert(reading) {
  return reading.alert === true || String(reading.alert_status || "").toUpperCase() === "ALERT" || ["Poor", "Hazardous"].includes(getStatus(reading));
}

function setBackendStatus(ok, message) {
  const card = $("backendStatus");
  const dot = card.querySelector(".status-dot");
  dot.className = `status-dot ${ok ? "ok" : "bad"}`;
  card.querySelector("strong").textContent = ok ? "Backend connected" : "Backend not connected";
  card.querySelector("small").textContent = message || backendUrl;
}

function toast(message, error = false) {
  const box = $("toast");
  box.textContent = message;
  box.className = `toast ${error ? "error" : ""}`;
  window.clearTimeout(box._hideTimer);
  box._hideTimer = window.setTimeout(() => box.classList.add("hidden"), 5000);
}

function updateCards(reading) {
  const status = getStatus(reading);
  const klass = statusClass(status);
  const main = $("mainStatusCard");
  main.className = `metric-card wide status-${klass}`;

  $("pollutionStatus").textContent = status || "--";
  $("alertMessage").textContent = reading.message || (isAlert(reading) ? "Alert: pollution level crossed the safe limit." : "Air quality is within configured limits.");

  $("aqiValue").textContent = formatNumber(reading.aqi ?? reading.air_quality_value ?? reading.airQualityValue, 0);
  $("pm25Value").textContent = formatNumber(reading.pm25 ?? reading.pm2_5, 1);
  $("pm10Value").textContent = formatNumber(reading.pm10, 1);
  $("gasValue").textContent = formatNumber(reading.gas ?? reading.air_quality ?? reading.airQuality, 0);
  $("co2Value").textContent = formatNumber(reading.co2, 0);
  $("coValue").textContent = formatNumber(reading.co, 1);
  $("temperatureValue").textContent = formatNumber(reading.temperature ?? reading.temp, 1);
  $("humidityValue").textContent = formatNumber(reading.humidity ?? reading.hum, 1);
}

function updateTable(rows) {
  const body = $("logsBody");
  const latestRows = rows.slice(-15).reverse();
  if (!latestRows.length) {
    body.innerHTML = `<tr><td colspan="9">No readings yet.</td></tr>`;
    return;
  }
  body.innerHTML = latestRows.map((r) => {
    const status = getStatus(r);
    const alert = isAlert(r) ? "ALERT" : "NORMAL";
    return `<tr>
      <td>${formatTime(r.timestamp)}</td>
      <td>${formatNumber(r.aqi ?? r.air_quality_value, 0)}</td>
      <td>${formatNumber(r.pm25, 1)}</td>
      <td>${formatNumber(r.pm10, 1)}</td>
      <td>${formatNumber(r.gas ?? r.air_quality, 0)}</td>
      <td>${formatNumber(r.temperature ?? r.temp, 1)} °C</td>
      <td>${formatNumber(r.humidity ?? r.hum, 1)} %</td>
      <td><span class="badge ${statusClass(status)}">${status}</span></td>
      <td><span class="badge ${alert === "ALERT" ? "alert" : "normal"}">${alert}</span></td>
    </tr>`;
  }).join("");
}

function formatTime(value) {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

function drawLineChart(canvas, rows, series, title) {
  const ctx = canvas.getContext("2d");
  const width = canvas.width = canvas.clientWidth * window.devicePixelRatio;
  const height = canvas.height = canvas.clientHeight * window.devicePixelRatio;
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  ctx.clearRect(0, 0, w, h);
  ctx.font = "12px Segoe UI, Arial";
  ctx.fillStyle = "#64748b";
  ctx.fillText(title, 18, 24);

  const chartX = 42, chartY = 42, chartW = w - 64, chartH = h - 70;
  ctx.strokeStyle = "#d9e2ec";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = chartY + (chartH / 4) * i;
    ctx.beginPath(); ctx.moveTo(chartX, y); ctx.lineTo(chartX + chartW, y); ctx.stroke();
  }
  ctx.beginPath(); ctx.moveTo(chartX, chartY); ctx.lineTo(chartX, chartY + chartH); ctx.lineTo(chartX + chartW, chartY + chartH); ctx.stroke();

  const dataRows = rows.slice(-30);
  const values = [];
  series.forEach(s => dataRows.forEach(r => values.push(number(r[s.key], 0))));
  const min = Math.min(0, ...values);
  const max = Math.max(10, ...values) * 1.1;

  series.forEach((s, index) => {
    ctx.strokeStyle = s.color;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    dataRows.forEach((row, i) => {
      const x = chartX + (dataRows.length === 1 ? chartW : (chartW / (dataRows.length - 1)) * i);
      const y = chartY + chartH - ((number(row[s.key], 0) - min) / (max - min)) * chartH;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();

    ctx.fillStyle = s.color;
    ctx.fillRect(chartX + index * 130, h - 22, 10, 10);
    ctx.fillStyle = "#334155";
    ctx.fillText(s.label, chartX + 15 + index * 130, h - 13);
  });
}

function updateCharts(rows) {
  const normalized = rows.map(r => ({
    ...r,
    aqi: number(r.aqi ?? r.air_quality_value, 0),
    temperature: number(r.temperature ?? r.temp, 0),
    humidity: number(r.humidity ?? r.hum, 0)
  }));
  drawLineChart(aqiCanvas, normalized, [{ key: "aqi", label: "AQI", color: "#2563eb" }], "AQI values");
  drawLineChart(envCanvas, normalized, [
    { key: "temperature", label: "Temperature", color: "#dc2626" },
    { key: "humidity", label: "Humidity", color: "#16a34a" }
  ], "Temperature and humidity");
}

async function refreshDashboard(showOkToast = false) {
  try {
    const [latestPayload, logsPayload] = await Promise.all([
      apiJson("/api/latest"),
      apiJson("/api/readings?limit=100")
    ]);
    const latest = unwrapReading(latestPayload);
    const rows = unwrapRows(logsPayload);
    updateCards(latest);
    updateTable(rows.length ? rows : [latest]);
    updateCharts(rows.length ? rows : [latest]);
    setBackendStatus(true, cleanUrl(backendUrl));
    if (showOkToast) toast("Backend connected and dashboard refreshed.");
  } catch (err) {
    setBackendStatus(false, "Start backend on http://127.0.0.1:8000");
    updateCards(demoRows[demoRows.length - 1]);
    updateTable(demoRows);
    updateCharts(demoRows);
    toast(`Backend connection error: ${err.message}. Demo data is shown until backend starts.`, true);
  }
}

async function simulate(mode) {
  try {
    const payload = await apiJson("/api/simulate", {
      method: "POST",
      body: JSON.stringify({ mode, count: 1 })
    });
    const reading = unwrapReading(payload);
    updateCards(reading);
    toast(`${mode.toUpperCase()} simulation reading generated.`);
    await refreshDashboard(false);
  } catch (err) {
    toast(`Simulation failed: ${err.message}`, true);
  }
}

function formToObject(form) {
  return Object.fromEntries([...new FormData(form).entries()].map(([key, value]) => [key, value === "" ? "" : Number(value)]));
}

async function saveManual(event) {
  event.preventDefault();
  try {
    const payload = formToObject(event.currentTarget);
    await apiJson("/api/manual", { method: "POST", body: JSON.stringify(payload) });
    toast("Manual reading saved successfully.");
    await refreshDashboard(false);
  } catch (err) {
    toast(`Manual reading failed: ${err.message}`, true);
  }
}

async function saveThresholds(event) {
  event.preventDefault();
  try {
    const payload = formToObject(event.currentTarget);
    await apiJson("/api/thresholds", { method: "POST", body: JSON.stringify(payload) });
    toast("Thresholds saved successfully.");
    await refreshDashboard(false);
  } catch (err) {
    toast(`Threshold save failed: ${err.message}`, true);
  }
}

async function loadThresholds() {
  try {
    const payload = await apiJson("/api/thresholds");
    const thresholds = payload.thresholds || payload;
    const form = $("thresholdForm");
    Object.entries(thresholds).forEach(([key, value]) => {
      if (form.elements[key]) form.elements[key].value = value;
    });
  } catch (_) {
    // Keep default values if backend is not running.
  }
}

async function clearLogs() {
  if (!confirm("Clear all backend CSV logs?")) return;
  try {
    await apiJson("/api/clear-logs", { method: "POST", body: JSON.stringify({}) });
    toast("Logs cleared successfully.");
    await refreshDashboard(false);
  } catch (err) {
    toast(`Clear logs failed: ${err.message}`, true);
  }
}

function download(path) {
  window.open(api(path), "_blank");
}

function setup() {
  aqiCanvas = $("aqiChart");
  envCanvas = $("envChart");
  $("backendUrl").value = backendUrl;

  $("saveBackendBtn").addEventListener("click", () => {
    backendUrl = cleanUrl($("backendUrl").value);
    localStorage.setItem("airQualityBackendUrl", backendUrl);
    toast("Backend URL saved.");
    refreshDashboard(true);
  });
  $("testBtn").addEventListener("click", () => {
    backendUrl = cleanUrl($("backendUrl").value);
    localStorage.setItem("airQualityBackendUrl", backendUrl);
    refreshDashboard(true);
  });
  $("refreshBtn").addEventListener("click", () => refreshDashboard(true));
  document.querySelectorAll(".scenario").forEach(btn => btn.addEventListener("click", () => simulate(btn.dataset.mode)));
  $("manualForm").addEventListener("submit", saveManual);
  $("thresholdForm").addEventListener("submit", saveThresholds);
  $("clearBtn").addEventListener("click", clearLogs);
  $("csvBtn").addEventListener("click", () => download("/api/export/csv"));
  $("pdfBtn").addEventListener("click", () => download("/api/export/pdf"));
  window.addEventListener("resize", () => refreshDashboard(false));

  loadThresholds();
  refreshDashboard(false);
  window.setInterval(() => refreshDashboard(false), 10000);
}

document.addEventListener("DOMContentLoaded", setup);
