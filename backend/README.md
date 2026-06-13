# Air Quality Backend

Correct backend for **IoT-Based Air Quality & Pollution Monitoring Dashboard**.

## Folder name
Keep this folder name exactly:

```text
air_quality_backend
```

Expected full Windows path:

```text
C:\Projects\IOT\Internet of Things - IoT-Based Air Quality & Pollution Monitoring Dashboard\air_quality_backend
```

## Run backend

Open PowerShell and run:

```powershell
cd "C:\Projects\IOT\Internet of Things - IoT-Based Air Quality & Pollution Monitoring Dashboard\air_quality_backend"
.\run_backend.bat
```

Keep this backend window open.

Backend URL:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Main frontend-safe endpoints

This backend includes multiple endpoint aliases so your dashboard will not show `detail: Not Found`.

```text
GET  /
GET  /health
GET  /api/health
GET  /api/status
GET  /api/latest
GET  /api/readings/latest
GET  /api/readings
GET  /api/logs
GET  /api/chart-data
GET  /api/summary
GET  /api/dashboard-summary
GET  /api/alerts
POST /api/readings
POST /api/manual
POST /api/save-reading
POST /api/simulate
POST /api/generate-simulation
GET  /api/export/csv
GET  /api/export/pdf
POST /api/clear-logs
GET  /api/thresholds
POST /api/thresholds
```

## Manual reading example

```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/manual" -ContentType "application/json" -Body '{"aqi":85,"pm25":45,"pm10":80,"gas":250,"temperature":30,"humidity":55}'
```

## Simulation example

```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/simulate" -ContentType "application/json" -Body '{"mode":"hazardous"}'
```

Simulation modes:

```text
normal
moderate
poor
hazardous
```

## Data files

```text
data/air_quality_logs.csv
data/thresholds.json
```

## Notes

- CORS is enabled for frontend use.
- CSV and PDF export are included.
- No API key is required.
- Works with virtual simulation, so hardware is not required.
