# Internet of Things - IoT-Based Air Quality & Pollution Monitoring Dashboard

## 📌 Project Overview

The **IoT-Based Air Quality & Pollution Monitoring Dashboard** is a real-time IoT system designed to monitor environmental air quality and pollution levels using sensors or virtual simulation.

This project measures important air quality parameters such as:

* AQI
* PM2.5
* PM10
* MQ135 gas value
* CO₂
* CO
* Temperature
* Humidity

The project supports both **hardware implementation** and **virtual simulation**, so it can be demonstrated even without physical ESP32, MQ135, DHT11/DHT22, or PM sensors.

---

## 🎯 Objective

The main objective of this project is to design and implement an IoT-based air quality monitoring system that can:

* Monitor air pollution in real time
* Display sensor values on a web dashboard
* Classify air quality as Good, Moderate, Poor, or Hazardous
* Generate alerts when pollution crosses safe limits
* Store sensor readings in logs
* Export reports in CSV and PDF formats
* Help students demonstrate IoT concepts in a GitHub-ready project

---

## 🏭 Problem Statement

Air pollution is a serious issue in cities, schools, hospitals, industries, and residential areas. Traditional air quality monitoring systems are often expensive and not easily available for small-scale use.

This project solves the problem by creating a low-cost IoT-based dashboard that continuously monitors air quality and alerts users when pollution becomes unsafe.

---

## ✅ Features

* Real-time air quality dashboard
* AQI monitoring
* PM2.5 and PM10 monitoring
* MQ135 gas value monitoring
* CO₂ and CO monitoring
* Temperature and humidity monitoring
* Virtual simulation for students without hardware
* Manual sensor value entry
* Threshold-based alert system
* Custom threshold settings
* Recent air quality logs
* AQI trend chart
* Environment trend chart
* CSV report download
* PDF report download
* FastAPI backend
* HTML, CSS, and JavaScript frontend
* Beginner-friendly and GitHub-ready structure

---

## 🧠 Working Principle

The system collects air quality data from sensors or virtual simulation. The backend processes the data, compares it with threshold values, classifies the air quality, generates alerts, and sends the processed data to the frontend dashboard.

```text
Sensors / Virtual Simulation
        ↓
Backend Data Processing
        ↓
AQI Classification
        ↓
Threshold Checking
        ↓
Alert Generation
        ↓
Dashboard Visualization
        ↓
CSV / PDF Report Generation
```

---

## 🧩 System Architecture

```text
+-----------------------------+
| ESP32 / Virtual Simulation  |
+-------------+---------------+
              |
              v
+-----------------------------+
| FastAPI Backend             |
| - Sensor data processing    |
| - AQI classification        |
| - Alert generation          |
| - CSV/PDF report export     |
+-------------+---------------+
              |
              v
+-----------------------------+
| Web Dashboard               |
| - Live values               |
| - Charts                    |
| - Alerts                    |
| - Logs                      |
| - Reports                   |
+-----------------------------+
```

---

## 🛠️ Technologies Used

### Hardware

* ESP32 / Arduino UNO
* MQ135 air quality sensor
* DHT11 / DHT22 temperature and humidity sensor
* Optional MQ2 gas sensor
* Optional buzzer
* Optional LED indicators
* Optional OLED/LCD display
* Power supply

### Software

* Python
* FastAPI
* Uvicorn
* HTML
* CSS
* JavaScript
* Chart.js
* CSV logging
* PDF report generation

---

## 📁 Project Folder Structure

```text
IoT-Air-Quality-Pollution-Monitoring-Dashboard/
│
├── air_quality_backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── run_backend.bat
│   ├── data/
│   └── reports/
│
├── air_quality_frontend/
│   ├── index.html
│   ├── run_frontend.bat
│   └── assets/
│       ├── styles.css
│       └── app.js
│
├── arduino_code/
│   └── esp32_air_quality.ino
│
├── images/
│   └── dashboard_screenshots/
│
├── circuit_diagram/
│   └── circuit.png
│
├── docs/
│   └── project_report.md
│
├── README.md
└── .gitignore
```

---

## 🔌 Hardware Components

| Component    | Purpose                                             |
| ------------ | --------------------------------------------------- |
| ESP32        | Reads sensor values and sends data to backend/cloud |
| MQ135        | Detects air quality and harmful gases               |
| DHT11/DHT22  | Measures temperature and humidity                   |
| MQ2          | Optional smoke or gas detection                     |
| Buzzer       | Gives alert when pollution is high                  |
| LED          | Indicates air quality status                        |
| OLED/LCD     | Optional local display                              |
| Power Supply | Provides power to the circuit                       |

---

## 🔗 Circuit Connection

### ESP32 to MQ135

| MQ135 Pin | ESP32 Pin |
| --------- | --------- |
| VCC       | 5V        |
| GND       | GND       |
| AO        | GPIO 34   |

### ESP32 to DHT11/DHT22

| DHT Pin | ESP32 Pin |
| ------- | --------- |
| VCC     | 3.3V      |
| GND     | GND       |
| DATA    | GPIO 4    |

### ESP32 to Buzzer

| Buzzer Pin | ESP32 Pin |
| ---------- | --------- |
| Positive   | GPIO 18   |
| Negative   | GND       |

### ESP32 to LED

| LED Pin  | ESP32 Pin                |
| -------- | ------------------------ |
| Positive | GPIO 19 through resistor |
| Negative | GND                      |

---

## 🚀 Backend Setup

### Step 1: Open PowerShell

```powershell
cd "C:\Projects\IOT\Internet of Things - IoT-Based Air Quality & Pollution Monitoring Dashboard\air_quality_backend"
```

### Step 2: Run Backend

```powershell
.\run_backend.bat
```

If PowerShell blocks the batch file, run:

```powershell
cmd /c run_backend.bat
```

### Step 3: Backend URL

```text
http://127.0.0.1:8000
```

### Step 4: Test Backend

Open this URL in browser:

```text
http://127.0.0.1:8000/api/latest
```

---

## 🌐 Frontend Setup

### Step 1: Open Another PowerShell Window

```powershell
cd "C:\Projects\IOT\Internet of Things - IoT-Based Air Quality & Pollution Monitoring Dashboard\air_quality_frontend"
```

### Step 2: Run Frontend

```powershell
.\run_frontend.bat
```

### Step 3: Open Dashboard

```text
http://127.0.0.1:5500
```

---

## ▶️ Correct Running Order

```text
1. Start backend first
2. Start frontend second
3. Keep both terminal windows open
4. Open dashboard in browser
```

---

## 📡 API Endpoints

| Method | Endpoint          | Description                     |
| ------ | ----------------- | ------------------------------- |
| GET    | `/`               | Backend welcome route           |
| GET    | `/health`         | Backend health check            |
| GET    | `/api/latest`     | Get latest sensor reading       |
| GET    | `/api/readings`   | Get all readings                |
| GET    | `/api/chart-data` | Get chart data                  |
| GET    | `/api/summary`    | Get dashboard summary           |
| POST   | `/api/simulate`   | Generate virtual sensor reading |
| POST   | `/api/manual`     | Save manual reading             |
| POST   | `/api/thresholds` | Update threshold values         |
| GET    | `/api/export/csv` | Download CSV report             |
| GET    | `/api/export/pdf` | Download PDF report             |
| DELETE | `/api/clear`      | Clear sensor logs               |

---

## 🧪 Virtual Simulation

This project includes virtual simulation for students who do not have real hardware.

Simulation modes:

* Normal
* Moderate
* Poor
* Hazardous

Example simulated output:

```text
AQI: 132
PM2.5: 72.0 µg/m³
PM10: 130 µg/m³
Gas: 410
CO₂: 1200 ppm
CO: 10.5 ppm
Temperature: 33.0 °C
Humidity: 49.0 %
Status: Poor
Alert: ALERT
```

---

## 🚨 Alert Logic

The system checks whether sensor values cross safe threshold limits.

Default thresholds:

| Parameter   | Limit     |
| ----------- | --------- |
| AQI         | 100       |
| PM2.5       | 60 µg/m³  |
| PM10        | 100 µg/m³ |
| Gas         | 350       |
| CO₂         | 1000 ppm  |
| CO          | 9 ppm     |
| Temperature | 45 °C     |
| Humidity    | 80%       |

If any value crosses the limit, an alert is generated.

Example:

```text
ALERT: AQI 132 > 100; PM2.5 72.0 > 60.0; Gas 410 > 350
```

---

## 📊 Dashboard

The dashboard displays:

* Backend connection status
* Latest air quality status
* AQI value
* PM2.5 value
* PM10 value
* MQ135 gas value
* CO₂ value
* CO value
* Temperature
* Humidity
* AQI trend chart
* Environment trend chart
* Recent logs
* Simulation buttons
* Manual reading form
* Threshold settings
* CSV and PDF download buttons

---

## 📄 Report Generation

The system can generate reports in:

* CSV format
* PDF format

Report contains:

* Timestamp
* AQI
* PM2.5
* PM10
* Gas value
* CO₂
* CO
* Temperature
* Humidity
* Status
* Alert message

---



## 🧑‍💻 ESP32 Arduino Code Example

```cpp
#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT11
#define MQ135_PIN 34
#define BUZZER_PIN 18
#define LED_PIN 19

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(MQ135_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  Serial.println("IoT Air Quality Monitoring System Started");
}

void loop() {
  int gasValue = analogRead(MQ135_PIN);
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  String status;

  if (gasValue < 200) {
    status = "Good";
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
  } else if (gasValue < 350) {
    status = "Moderate";
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
  } else if (gasValue < 500) {
    status = "Poor";
    digitalWrite(BUZZER_PIN, HIGH);
    digitalWrite(LED_PIN, HIGH);
  } else {
    status = "Hazardous";
    digitalWrite(BUZZER_PIN, HIGH);
    digitalWrite(LED_PIN, HIGH);
  }

  Serial.println("-----------------------------");
  Serial.print("Gas Value: ");
  Serial.println(gasValue);

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  Serial.print("Air Quality Status: ");
  Serial.println(status);

  delay(3000);
}
```

---

## 📌 Applications

This project can be used in:

* Smart cities
* Schools and colleges
* Hospitals
* Industrial plants
* Smart homes
* Environmental monitoring stations
* Pollution monitoring systems
* Student IoT projects

---

## 🎓 Learning Outcomes

After completing this project, you will understand:

* IoT system design
* Sensor data collection
* Air quality monitoring
* AQI classification
* Backend API development
* Frontend dashboard development
* Alert generation
* Data logging
* CSV and PDF report generation
* GitHub project documentation

---

## 🔮 Future Improvements

* Add real ESP32 Wi-Fi data transmission
* Add MQTT protocol support
* Add ThingSpeak or Blynk cloud dashboard
* Add mobile app alerts
* Add email or SMS notifications
* Add GPS-based pollution mapping
* Add multiple sensor nodes
* Add AI-based pollution prediction
* Add solar-powered deployment
* Add database integration

---

Interview Question and Answer

-- 1. Interview Question: Explain your IoT-Based Air Quality & Pollution Monitoring Dashboard project.
-- Answer:
-- In this project, I built an IoT-based air quality monitoring system that measures pollution-related values using sensors such as MQ135 and environmental values like temperature and humidity using DHT11 or DHT22. The system processes sensor readings, classifies air quality as Good, Moderate, Poor, or Hazardous, generates alerts when pollution crosses a threshold, and displays the data on a dashboard. This project demonstrates IoT concepts like sensor data collection, microcontroller processing, cloud dashboard integration, alert generation, and environmental monitoring.

-- 2. Interview Question: What problem does this project solve?
-- Answer:
-- This project solves the problem of monitoring air pollution manually. It helps users track air quality in real time and receive alerts when pollution levels become unsafe.

-- 3. Interview Question: Which sensors are used in this project?
-- Answer:
-- This project can use an MQ135 sensor for air quality detection, MQ2 sensor for smoke or gas detection, and DHT11 or DHT22 sensor for temperature and humidity monitoring.

-- 4. Interview Question: Which microcontroller can be used?
-- Answer:
-- ESP32 is recommended because it has built-in Wi-Fi, which makes it easy to send sensor data to a cloud dashboard. Arduino UNO can also be used for a basic version, but it may require an extra Wi-Fi module.

-- 5. Interview Question: How does the air quality alert system work?
-- Answer:
-- The system reads pollution sensor values and compares them with predefined threshold levels. If the value crosses the safe limit, the system triggers an alert using buzzer, LED, dashboard notification, or message output.

-- 6. Interview Question: How is IoT used in this project?
-- Answer:
-- IoT is used by collecting air quality data from sensors and sending it to a cloud dashboard where users can monitor pollution levels remotely in real time.

-- 7. Interview Question: What output does the project generate?
-- Answer:
-- The project generates air quality values, temperature, humidity, pollution category, alert status, dashboard graphs, and CSV logs for historical analysis.

-- 8. Interview Question: Why is data logging important in this project?
-- Answer:
-- Data logging helps store pollution readings over time. This allows users to analyze air quality trends, compare pollution levels, and identify unsafe periods.

-- 9. Interview Question: What challenges did you face in this project?
-- Answer:
-- The main challenges were setting correct threshold values, handling fluctuating sensor readings, simulating realistic pollution data, integrating dashboard updates, and avoiding false alerts.

-- 10. Interview Question: How can this project be improved further?
-- Answer:
-- This project can be improved by adding multiple gas sensors, GPS-based pollution mapping, mobile app alerts, AQI calculation using standard formulas, AI-based pollution prediction, solar-powered deployment, and real-time cit

---

## 👨‍🎓 Author

**Prasad Shelar**


---

## 📜 License

This project is created for educational and academic purposes. You can use and modify it for learning, college submissions, and portfolio projects.
