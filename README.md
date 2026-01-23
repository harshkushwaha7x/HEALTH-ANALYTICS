<div align="center">

# HEALTH ANALYTICS

**Health Analytics** is a full-stack AI-powered health dashboard built with modern web technologies. It enables **multi-modal data analysis**, **machine learning predictions**, and **real-time health insights** — designed for individuals who want to understand and track their health data intelligently.

[Portfolio](https://portfolio-harsh7x.vercel.app/) • [GitHub](https://github.com/harshkushwaha7x)

</div>

---

<p align="center">
  <a href="https://github.com/harshkushwaha7x"><img src="https://img.shields.io/github/last-commit/harshkushwaha7x/health-analytics?style=flat-square" alt="last commit"></a>
  <a href="https://github.com/harshkushwaha7x"><img src="https://img.shields.io/badge/Python-Flask-blue?style=flat-square" alt="python"></a>
  <a href="https://github.com/harshkushwaha7x"><img src="https://img.shields.io/badge/React-Vite-purple?style=flat-square" alt="react"></a>
  <a href="#"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="license" /></a>
  <img src="https://img.shields.io/badge/version-1.0.0-success?style=flat-square" alt="version" />
</p>

---

## Overview

**Health Analytics** is a comprehensive health data platform that processes lab reports, medical images, genomics data, and clinical notes to generate AI-driven insights and risk predictions.

Built using **Flask**, **React**, **SQLite**, and **Machine Learning models**, it delivers intelligent health analysis with explainable predictions.

Core highlights:

* **AI-Powered Predictions**: Multi-modal ML models for health risk assessment
* **Interactive Dashboard**: Real-time visualizations and trend charts
* **Multi-Format Upload**: PDF, CSV, Excel, VCF, and medical images
* **Comprehensive Analysis**: Labs, imaging, genomics, and clinical notes
* **Trend Tracking**: Historical data visualization with sparklines

---

## Screenshots

### Dashboard
<img src="assets/HEALTH ANALYTICS 1.png" alt="Dashboard" width="100%">

### Results
<img src="assets/HEALTH ANALYTICS 2.png" alt="Results" width="100%">

### AI Recommendations
<img src="assets/HEALTH ANALYTICS 3.png" alt="AI Recommendations" width="100%">

---

## Solution Architecture

<img src="assets/solution_architecture.png" alt="Solution Architecture" width="100%">

---

## Key Features

### Machine Learning Models

* **Diabetes Risk Model**: A1C-based classification with clinical thresholds
* **Cardiovascular Risk**: Framingham-inspired lipid panel analysis
* **Imaging Classifier**: Abnormality detection for X-rays, CT, MRI with cancer staging
* **Clinical NLP**: Entity extraction from doctor's notes
* **Genomics Analysis**: ACMG variant classification and hereditary syndrome detection
* **Anomaly Detection**: Trend analysis, rate of change, clinical reference ranges
* **Multi-Modal Fusion**: Combined health risk assessment

### Dashboard & Visualization

* Overall health risk score with confidence intervals
* Interactive trend charts for biomarkers
* Color-coded status indicators (Normal/High/Low)
* Predictions panel with contributing factors
* Personalized health recommendations

### Data Ingestion

* PDF lab reports with OCR extraction
* CSV/Excel spreadsheet processing
* Medical image upload and analysis
* VCF genomics file parsing
* Clinical notes text processing

---

## Tech Stack

### Frontend

* React 18 + Vite
* Custom CSS (Dark Theme)
* Canvas API Charts
* Lucide React Icons
* Axios HTTP Client

### Backend

* Python Flask + Flask-CORS
* SQLAlchemy ORM
* SQLite Database
* scikit-learn & XGBoost
* PyMuPDF & Pandas
* Pillow & OpenCV

### AI/ML

* Diabetes Risk Classifier
* Cardiovascular Risk Model
* Imaging CNN Simulator
* Clinical NLP Processor
* Genomics Variant Analyzer
* Multi-Modal Fusion Engine

---

## Architecture

```text
Health-Analytics/
├── backend/
│   ├── app.py              # Flask API server (34 endpoints)
│   ├── models.py           # SQLAlchemy database models
│   ├── ml_models.py        # 7 ML model classes
│   ├── parsers.py          # Multi-format file parsing
│   ├── llm_service.py      # AI/LLM integration
│   ├── data_generator.py   # Synthetic data generation
│   ├── requirements.txt    # Python dependencies
│   └── uploads/            # File upload storage
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main application
│   │   ├── index.css       # Global styles (Teal theme)
│   │   └── components/
│   │       ├── Dashboard.jsx
│   │       ├── TrendChart.jsx
│   │       ├── LabsPanel.jsx
│   │       ├── PredictionsPanel.jsx
│   │       ├── GenomicsPanel.jsx
│   │       ├── ImagingPanel.jsx
│   │       ├── NotesPanel.jsx
│   │       ├── FileUpload.jsx
│   │       ├── Header.jsx
│   │       ├── PatientSelector.jsx
│   │       ├── ReportsView.jsx
│   │       └── TrendsView.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

* Python 3.8+
* Node.js 18+
* npm or yarn

### Installation

```bash
git clone https://github.com/harshkushwaha7x/HEALTH-ANALYTICS.git
cd health-analytics
```

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

**API Configuration**

This project integrates with **Google Gemini** and **Groq** APIs for AI features:

| API | Purpose | Get Key |
|-----|---------|---------|
| **Gemini** | Lab report text extraction, Health recommendations | [Google AI Studio](https://aistudio.google.com/apikey) |
| **Groq** | Medical image analysis (X-Ray/CT/MRI) | [Groq Console](https://console.groq.com/keys) |

**Set environment variables in terminal before running backend:**

**Windows (CMD):**
```bash
set GEMINI_API_KEY=your_gemini_api_key_here
set GROQ_API_KEY=your_groq_api_key_here
python app.py
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_gemini_api_key_here"
$env:GROQ_API_KEY="your_groq_api_key_here"
python app.py
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY=your_gemini_api_key_here
export GROQ_API_KEY=your_groq_api_key_here
python app.py
```

Backend runs at `http://localhost:5000`

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:3000`

---

## API Endpoints

### Patients

* `GET /api/patients` — List all patients
* `GET /api/patients/:id` — Get patient details
* `POST /api/patients` — Create new patient
* `PUT /api/patients/:id` — Update patient
* `DELETE /api/patients/:id` — Delete patient

### Dashboard

* `GET /api/patients/:id/dashboard` — Complete dashboard data
* `GET /api/patients/:id/labs` — Lab results
* `GET /api/patients/:id/labs/trends` — Lab trends for charts

### Predictions

* `POST /api/patients/:id/predict` — Run ML predictions
* `GET /api/patients/:id/predictions` — Get predictions

### File Upload

* `POST /api/patients/:id/upload` — Upload health file

### Export

* `GET /api/patients/:id/export?format=text` — Export report as TXT

---

## ML Models

| Model | Input | Output |
|-------|-------|--------|
| Diabetes Risk | A1C, Glucose, BMI | Risk Score, Classification |
| Cardiovascular | LDL, HDL, BP, Age | 10-Year CVD Risk |
| Imaging | X-ray, CT, MRI | Abnormality Score, Findings |
| Clinical NLP | Doctor's Notes | Conditions, Medications |
| Genomics | VCF Variants | Pathogenicity, Cancer Risk |
| Fusion | All Modalities | Overall Health Score |

---

## Performance

* Lightweight SQLite database
* Efficient Canvas-based charts
* Lazy loading components
* Optimized API responses
* Responsive design

---

## Design

* **Theme**: Professional Teal/Slate dark mode
* **Typography**: Inter font family
* **Components**: Glassmorphism effects
* **Charts**: Custom Canvas visualizations
* **Icons**: Lucide React

---

## Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m "Add new feature"`)
4. Push & open a Pull Request

---

## Disclaimer

This application is for **educational and demonstration purposes only**. It is NOT intended for clinical use or medical decision-making. Always consult qualified healthcare professionals for medical advice.

---

## Contact

**Harsh Kushwaha** — Developer & Maintainer

* Portfolio: [https://portfolio-harsh7x.vercel.app/](https://portfolio-harsh7x.vercel.app/)
* GitHub: [https://github.com/harshkushwaha7x](https://github.com/harshkushwaha7x)
* LinkedIn: [https://www.linkedin.com/in/harsh-kushwaha-7x/](https://www.linkedin.com/in/harsh-kushwaha-7x/)
* Email: [harshkushwaha4151@gmail.com](mailto:harshkushwaha4151@gmail.com)

---

<div align="center">

**HEALTH ANALYTICS** – AI-Powered Health Insights. Track Smarter.
Built by <b>Harsh Kushwaha</b>

</div>
