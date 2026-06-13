from __future__ import annotations

import csv
import io
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
CSV_FILE = DATA_DIR / "air_quality_logs.csv"
THRESHOLD_FILE = DATA_DIR / "thresholds.json"

CSV_FIELDS = [
    "timestamp",
    "aqi",
    "air_quality",
    "air_quality_value",
    "pm25",
    "pm10",
    "gas",
    "co2",
    "co",
    "temperature",
    "humidity",
    "pollution_status",
    "category",
    "alert_status",
    "alert",
    "message",
]

DEFAULT_THRESHOLDS = {
    "max_aqi": 100,
    "max_pm25": 60,
    "max_pm10": 100,
    "max_gas": 350,
    "max_co2": 1000,
    "max_co": 9,
    "max_temperature": 45,
    "min_humidity": 20,
    "max_humidity": 80,
}

app = FastAPI(
    title="IoT Air Quality & Pollution Monitoring Backend",
    description="FastAPI backend for AQI simulation, manual readings, dashboard data, CSV logs and PDF reports.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def clean_mode(mode: Optional[str]) -> str:
    value = (mode or "normal").strip().lower().replace("_", "-")
    aliases = {
        "good": "normal",
        "safe": "normal",
        "medium": "moderate",
        "warning": "moderate",
        "high": "poor",
        "bad": "poor",
        "unhealthy": "poor",
        "smoke": "hazardous",
        "gas": "hazardous",
        "gas-leak": "hazardous",
        "leak": "hazardous",
        "danger": "hazardous",
        "critical": "hazardous",
    }
    return aliases.get(value, value if value in {"normal", "moderate", "poor", "hazardous"} else "normal")


def classify_aqi(aqi: float) -> str:
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 200:
        return "Poor"
    return "Hazardous"


def read_thresholds() -> Dict[str, float]:
    ensure_storage()
    try:
        data = json.loads(THRESHOLD_FILE.read_text(encoding="utf-8"))
        merged = {**DEFAULT_THRESHOLDS, **data}
        return {key: to_float(value, DEFAULT_THRESHOLDS.get(key, 0)) for key, value in merged.items()}
    except Exception:
        THRESHOLD_FILE.write_text(json.dumps(DEFAULT_THRESHOLDS, indent=2), encoding="utf-8")
        return dict(DEFAULT_THRESHOLDS)


def write_thresholds(data: Dict[str, Any]) -> Dict[str, float]:
    current = read_thresholds()
    for key, value in data.items():
        if key in DEFAULT_THRESHOLDS:
            current[key] = to_float(value, DEFAULT_THRESHOLDS[key])
    THRESHOLD_FILE.write_text(json.dumps(current, indent=2), encoding="utf-8")
    return current


def alert_message(reading: Dict[str, Any], thresholds: Dict[str, float]) -> str:
    reasons = []
    if reading["aqi"] > thresholds["max_aqi"]:
        reasons.append(f"AQI {reading['aqi']:.0f} > {thresholds['max_aqi']:.0f}")
    if reading["pm25"] > thresholds["max_pm25"]:
        reasons.append(f"PM2.5 {reading['pm25']:.1f} > {thresholds['max_pm25']:.1f}")
    if reading["pm10"] > thresholds["max_pm10"]:
        reasons.append(f"PM10 {reading['pm10']:.1f} > {thresholds['max_pm10']:.1f}")
    if reading["gas"] > thresholds["max_gas"]:
        reasons.append(f"Gas {reading['gas']:.0f} > {thresholds['max_gas']:.0f}")
    if reading["co2"] > thresholds["max_co2"]:
        reasons.append(f"CO2 {reading['co2']:.0f} > {thresholds['max_co2']:.0f}")
    if reading["co"] > thresholds["max_co"]:
        reasons.append(f"CO {reading['co']:.1f} > {thresholds['max_co']:.1f}")
    if reading["temperature"] > thresholds["max_temperature"]:
        reasons.append(f"Temperature {reading['temperature']:.1f} > {thresholds['max_temperature']:.1f}")
    if reading["humidity"] < thresholds["min_humidity"] or reading["humidity"] > thresholds["max_humidity"]:
        reasons.append("Humidity outside safe range")
    if reasons:
        return "ALERT: " + "; ".join(reasons)
    return "NORMAL: Air quality is within configured limits"


def normalize_reading(payload: Optional[Dict[str, Any]] = None, mode: Optional[str] = None) -> Dict[str, Any]:
    payload = payload or {}
    scenario = clean_mode(str(payload.get("mode") or payload.get("scenario") or mode or "normal"))

    ranges = {
        "normal": {"aqi": (20, 50), "pm25": (5, 25), "pm10": (15, 50), "gas": (90, 180), "co2": (380, 650), "co": (0.2, 3.0), "temp": (24, 31), "hum": (40, 65)},
        "moderate": {"aqi": (55, 100), "pm25": (26, 60), "pm10": (51, 100), "gas": (181, 320), "co2": (651, 950), "co": (3.1, 8.0), "temp": (27, 35), "hum": (35, 70)},
        "poor": {"aqi": (110, 200), "pm25": (61, 120), "pm10": (101, 220), "gas": (321, 520), "co2": (951, 1400), "co": (8.1, 15.0), "temp": (30, 40), "hum": (25, 75)},
        "hazardous": {"aqi": (210, 350), "pm25": (121, 250), "pm10": (221, 450), "gas": (521, 900), "co2": (1401, 2400), "co": (15.1, 35.0), "temp": (34, 48), "hum": (15, 85)},
    }
    r = ranges[scenario]

    def payload_float(*keys: str, default: float) -> float:
        for key in keys:
            if key in payload:
                return to_float(payload.get(key), default)
        return default

    random_aqi = random.uniform(*r["aqi"])
    pm25 = payload_float("pm25", "pm2_5", "PM25", default=random.uniform(*r["pm25"]))
    pm10 = payload_float("pm10", "PM10", default=random.uniform(*r["pm10"]))
    gas = payload_float("gas", "mq135", "mq135_raw", "air_quality", "airQuality", default=random.uniform(*r["gas"]))
    co2 = payload_float("co2", "CO2", default=random.uniform(*r["co2"]))
    co = payload_float("co", "CO", default=random.uniform(*r["co"]))
    temperature = payload_float("temperature", "temp", "Temperature", default=random.uniform(*r["temp"]))
    humidity = payload_float("humidity", "hum", "Humidity", default=random.uniform(*r["hum"]))

    # AQI can be passed directly. If not, estimate it from pollutant signals.
    aqi = payload_float("aqi", "AQI", "air_quality_value", "airQualityValue", default=random_aqi)
    if "aqi" not in {str(k).lower() for k in payload.keys()} and not any(k in payload for k in ["air_quality_value", "airQualityValue"]):
        estimated_from_pm25 = min(500, pm25 * 1.7)
        estimated_from_pm10 = min(500, pm10 * 0.8)
        estimated_from_gas = min(500, gas * 0.35)
        aqi = max(aqi, estimated_from_pm25, estimated_from_pm10, estimated_from_gas)

    aqi = round(max(0, aqi), 2)
    pm25 = round(max(0, pm25), 2)
    pm10 = round(max(0, pm10), 2)
    gas = round(max(0, gas), 2)
    co2 = round(max(0, co2), 2)
    co = round(max(0, co), 2)
    temperature = round(temperature, 2)
    humidity = round(max(0, min(100, humidity)), 2)
    category = classify_aqi(aqi)

    reading: Dict[str, Any] = {
        "timestamp": str(payload.get("timestamp") or now_iso()),
        "aqi": aqi,
        "air_quality": round(gas, 2),
        "air_quality_value": aqi,
        "pm25": pm25,
        "pm10": pm10,
        "gas": gas,
        "co2": co2,
        "co": co,
        "temperature": temperature,
        "humidity": humidity,
        "pollution_status": category,
        "category": category,
    }
    msg = alert_message(reading, read_thresholds())
    is_alert = msg.startswith("ALERT") or category in {"Poor", "Hazardous"}
    reading.update(
        {
            "alert_status": "ALERT" if is_alert else "NORMAL",
            "alert": is_alert,
            "message": msg,
            # Friendly aliases for different frontend naming styles.
            "status": category,
            "pollution_level": category,
            "temp": temperature,
            "hum": humidity,
            "airQuality": round(gas, 2),
            "airQualityValue": aqi,
        }
    )
    return reading


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if not THRESHOLD_FILE.exists():
        THRESHOLD_FILE.write_text(json.dumps(DEFAULT_THRESHOLDS, indent=2), encoding="utf-8")
    if not CSV_FILE.exists():
        with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()


def append_reading(reading: Dict[str, Any]) -> Dict[str, Any]:
    ensure_storage()
    row = {field: reading.get(field, "") for field in CSV_FIELDS}
    with CSV_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(row)
    return reading


def read_all_rows(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    ensure_storage()
    rows: List[Dict[str, Any]] = []
    with CSV_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = dict(row)
            for key in ["aqi", "air_quality", "air_quality_value", "pm25", "pm10", "gas", "co2", "co", "temperature", "humidity"]:
                cleaned[key] = to_float(cleaned.get(key), 0.0)
            cleaned["alert"] = str(cleaned.get("alert", "False")).lower() in {"true", "1", "yes", "alert"}
            cleaned["status"] = cleaned.get("category") or cleaned.get("pollution_status")
            cleaned["pollution_level"] = cleaned.get("pollution_status")
            cleaned["temp"] = cleaned.get("temperature")
            cleaned["hum"] = cleaned.get("humidity")
            cleaned["airQuality"] = cleaned.get("air_quality")
            cleaned["airQualityValue"] = cleaned.get("air_quality_value")
            rows.append(cleaned)
    if limit is not None and limit > 0:
        return rows[-limit:]
    return rows


def latest_or_seed() -> Dict[str, Any]:
    rows = read_all_rows()
    if rows:
        return rows[-1]
    return append_reading(normalize_reading(mode="normal"))


def clear_csv() -> Dict[str, Any]:
    ensure_storage()
    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
    return {"message": "Logs cleared successfully", "count": 0}


def generate_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        latest = latest_or_seed()
        rows = [latest]
    aqi_values = [to_float(row.get("aqi"), 0) for row in rows]
    alerts = [row for row in rows if str(row.get("alert_status", "")).upper() == "ALERT" or row.get("alert") is True]
    latest = rows[-1]
    return {
        "total_readings": len(rows),
        "alert_count": len(alerts),
        "latest": latest,
        "average_aqi": round(sum(aqi_values) / len(aqi_values), 2),
        "max_aqi": round(max(aqi_values), 2),
        "min_aqi": round(min(aqi_values), 2),
        "current_status": latest.get("pollution_status") or latest.get("category"),
        "current_alert_status": latest.get("alert_status"),
    }


def make_csv_response() -> StreamingResponse:
    ensure_storage()
    content = CSV_FILE.read_text(encoding="utf-8")
    return StreamingResponse(
        io.StringIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=air_quality_logs.csv"},
    )


def pdf_escape(text: Any) -> str:
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def minimal_pdf(lines: List[str]) -> bytes:
    y_start = 800
    text_commands = ["BT", "/F1 14 Tf", f"50 {y_start} Td"]
    first = True
    for line in lines[:42]:
        if first:
            first = False
        else:
            text_commands.append("0 -18 Td")
        text_commands.append(f"({pdf_escape(line)}) Tj")
    text_commands.append("ET")
    stream = "\n".join(text_commands).encode("latin-1", errors="replace")

    objects = []
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objects.append(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n")
    objects.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    objects.append(b"5 0 obj\n<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream\nendobj\n")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)
    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)+1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode())
    return bytes(pdf)


@app.on_event("startup")
def startup() -> None:
    ensure_storage()
    if not read_all_rows():
        for mode in ["normal", "normal", "moderate"]:
            append_reading(normalize_reading(mode=mode))


@app.get("/")
def root() -> Dict[str, Any]:
    latest = latest_or_seed()
    return {
        "message": "Air Quality Backend is running",
        "backend": "OK",
        "docs": "http://127.0.0.1:8000/docs",
        "health": "http://127.0.0.1:8000/health",
        "latest": latest,
    }


@app.get("/health")
@app.get("/api/health")
@app.get("/api/status")
def health() -> Dict[str, Any]:
    return {"status": "ok", "message": "Backend running", "latest": latest_or_seed()}


@app.get("/api/readings")
@app.get("/api/logs")
@app.get("/api/data")
@app.get("/readings")
@app.get("/data")
def get_readings(limit: int = Query(100, ge=1, le=10000)) -> Dict[str, Any]:
    rows = read_all_rows(limit=limit)
    return {"count": len(rows), "readings": rows, "data": rows, "logs": rows, "latest": rows[-1] if rows else latest_or_seed()}


@app.get("/api/readings/latest")
@app.get("/api/latest")
@app.get("/api/sensor-data")
@app.get("/api/air-quality-data")
@app.get("/latest")
@app.get("/sensor-data")
def get_latest() -> Dict[str, Any]:
    latest = latest_or_seed()
    return {"reading": latest, "latest": latest, "data": latest, **latest}


@app.post("/api/readings")
@app.post("/api/manual")
@app.post("/api/manual-reading")
@app.post("/api/save-reading")
@app.post("/add-reading")
def add_reading(payload: Dict[str, Any] = Body(default_factory=dict)) -> Dict[str, Any]:
    reading = normalize_reading(payload)
    append_reading(reading)
    return {"message": "Reading saved successfully", "reading": reading, "data": reading, **reading}


@app.post("/api/simulate")
@app.post("/api/generate-simulation")
@app.post("/api/generate")
def generate_simulation(payload: Dict[str, Any] = Body(default_factory=dict)) -> Dict[str, Any]:
    mode = clean_mode(str(payload.get("mode") or payload.get("scenario") or "normal"))
    count = int(to_float(payload.get("count"), 1))
    count = max(1, min(count, 500))
    readings = []
    for _ in range(count):
        reading = normalize_reading(payload={"mode": mode})
        append_reading(reading)
        readings.append(reading)
    return {"message": f"Generated {count} {mode} simulation reading(s)", "reading": readings[-1], "readings": readings, "data": readings[-1]}


@app.get("/api/simulate")
def generate_simulation_get(mode: str = Query("normal"), count: int = Query(1, ge=1, le=500)) -> Dict[str, Any]:
    readings = []
    for _ in range(count):
        reading = normalize_reading(mode=mode)
        append_reading(reading)
        readings.append(reading)
    return {"message": f"Generated {count} {clean_mode(mode)} simulation reading(s)", "reading": readings[-1], "readings": readings, "data": readings[-1]}


@app.get("/api/thresholds")
def get_thresholds() -> Dict[str, Any]:
    return {"thresholds": read_thresholds(), **read_thresholds()}


@app.post("/api/thresholds")
def set_thresholds(payload: Dict[str, Any] = Body(default_factory=dict)) -> Dict[str, Any]:
    thresholds = write_thresholds(payload)
    latest = latest_or_seed()
    return {"message": "Thresholds saved successfully", "thresholds": thresholds, "latest": latest}


@app.post("/api/clear-logs")
@app.delete("/api/readings")
@app.delete("/api/logs")
def clear_logs() -> Dict[str, Any]:
    return clear_csv()


@app.get("/api/export/csv")
@app.get("/api/download/csv")
@app.get("/api/csv")
def export_csv() -> StreamingResponse:
    return make_csv_response()


@app.get("/api/export/pdf")
@app.get("/api/download/pdf")
@app.get("/api/pdf")
def export_pdf() -> Response:
    rows = read_all_rows(limit=25)
    summary = generate_summary(rows)
    latest = summary["latest"]
    lines = [
        "IoT Air Quality & Pollution Monitoring Report",
        f"Generated: {now_iso()}",
        "",
        f"Total readings: {summary['total_readings']}",
        f"Alert count: {summary['alert_count']}",
        f"Average AQI: {summary['average_aqi']}",
        f"Max AQI: {summary['max_aqi']}",
        f"Min AQI: {summary['min_aqi']}",
        "",
        "Latest Reading",
        f"Timestamp: {latest.get('timestamp')}",
        f"AQI: {latest.get('aqi')}",
        f"PM2.5: {latest.get('pm25')}",
        f"PM10: {latest.get('pm10')}",
        f"Gas/MQ135: {latest.get('gas')}",
        f"CO2: {latest.get('co2')}",
        f"CO: {latest.get('co')}",
        f"Temperature: {latest.get('temperature')} C",
        f"Humidity: {latest.get('humidity')} %",
        f"Pollution Status: {latest.get('pollution_status')}",
        f"Alert Status: {latest.get('alert_status')}",
        f"Message: {latest.get('message')}",
        "",
        "Recent readings are stored in data/air_quality_logs.csv",
    ]
    pdf = minimal_pdf(lines)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=air_quality_report.pdf"},
    )


@app.get("/api/summary")
@app.get("/api/dashboard-summary")
def summary() -> Dict[str, Any]:
    rows = read_all_rows()
    return generate_summary(rows)


@app.get("/api/chart-data")
def chart_data(limit: int = Query(50, ge=1, le=1000)) -> Dict[str, Any]:
    rows = read_all_rows(limit=limit)
    return {
        "labels": [row.get("timestamp") for row in rows],
        "aqi": [row.get("aqi") for row in rows],
        "pm25": [row.get("pm25") for row in rows],
        "pm10": [row.get("pm10") for row in rows],
        "temperature": [row.get("temperature") for row in rows],
        "humidity": [row.get("humidity") for row in rows],
        "gas": [row.get("gas") for row in rows],
        "readings": rows,
    }


@app.get("/api/alerts")
def alerts(limit: int = Query(100, ge=1, le=1000)) -> Dict[str, Any]:
    rows = read_all_rows(limit=limit)
    alert_rows = [row for row in rows if str(row.get("alert_status", "")).upper() == "ALERT" or row.get("alert") is True]
    return {"count": len(alert_rows), "alerts": alert_rows}


@app.get("/api/cors-test")
def cors_test() -> Dict[str, str]:
    return {"message": "CORS is enabled"}
