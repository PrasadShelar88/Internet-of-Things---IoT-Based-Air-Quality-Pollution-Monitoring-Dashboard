# IoT Air Quality & Pollution Monitoring Dashboard - Frontend

This is the correct frontend for the FastAPI backend running at `http://127.0.0.1:8000`.

## Features

- Real-time AQI dashboard
- PM2.5 and PM10 cards
- MQ135 gas value card
- CO2 and CO cards
- Temperature and humidity cards
- Normal / Moderate / Poor / Hazardous simulation buttons
- Manual reading form
- Threshold settings form
- CSV export
- PDF report export
- Recent readings table
- Simple canvas charts without internet/CDN dependencies
- Demo fallback if backend is not running

## How to run

Open PowerShell:

```powershell
cd "C:\Projects\IOT\Internet of Things - IoT-Based Air Quality & Pollution Monitoring Dashboard\air_quality_frontend"
.\run_frontend.bat
```

Open browser:

```text
http://127.0.0.1:5500
```

## Required backend

Start backend first in another PowerShell window:

```powershell
cd "C:\Projects\IOT\Internet of Things - IoT-Based Air Quality & Pollution Monitoring Dashboard\air_quality_backend"
.\run_backend.bat
```

Backend URL:

```text
http://127.0.0.1:8000
```

## Files

```text
air_quality_frontend/
├── index.html
├── assets/
│   ├── styles.css
│   └── app.js
├── run_frontend.bat
├── CORRECT_FRONTEND_COMMANDS.txt
└── README.md
```
