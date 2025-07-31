# 🛡️ Fraud Detection System

A lightweight, real-time fraud detection API built with **FastAPI**, **async SQLAlchemy**, and a rule-based analysis engine. This project simulates financial transactions, detects suspicious activity, and provides fraud insights via a clean API and dashboard interface.

## Features
- Asynchronous FastAPI backend for high-performance request handling
- Rule-based fraud detection logic with customizable risk scoring
- Real-time transaction analysis with fraud score & recommendation
- Alerts panel for monitoring high-risk activity
- Comprehensive stats API for transaction and fraud overview
- PostgreSQL integration for reliable data persistence
- Realistic fake data generator for testing and development

---

## Tech Stack
- Backend: Python 3.11+, FastAPI, SQLAlchemy (async)
- Database: PostgreSQL with asyncpg driver
- Data Processing: Pandas
- Frontend: React.js with modern UI components
- API Documentation: Auto-generated OpenAPI/Swagger docs

---

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- Node.js and npm (for frontend)
- 
### Setup Instructions
1. Clone the repository
```bash
git clone https://github.com/Bothaina-Karakrah/fraud-detection-engine.git
cd fraud-detection-engine
```
2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```
3. Install Python dependencies
```bash
pip install -r requirements.txt
```
4. Install frontend dependencies
```bash
cd dashboard
npm install
cd ..
```
---

## 🗃️ Environment Configuration

Create a `.env` file in the root:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/fraud_detection

# API Configuration
API_HOST=localhost
API_PORT=8000
DEBUG=True
```

You can use `init_db.py` and `insert_sample_data.py` to set up tables and generate fake data.

---

## 🚀 Getting Started
1. Database Setup
```bash
# Create database tables
python init_db.py

# Generate sample transaction data
python insert_sample_data.py
```
2. Start the Backend Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The API will be available at http://localhost:8000 <br>
API documentation: http://localhost:8000/docs

3. Start the Frontend Dashboard
```bash
cd dashboard
npm run dev
```

![img.png](img.png)

---

## 📊 API Endpoints

- `GET /api/stats` – Overview of total transactions, frauds, fraud rate
- `GET /api/alerts/recent` – Recent triggered alerts
- `POST /api/transactions/analyze` – Analyze a transaction for fraud

---

---

## 📌 Project Status

✅ Core backend & analysis logic implemented  
✅ Dashboard with live alerts & analysis  
🚧 Machine learning support (planned)

---

## 👤 Author

Bothaina Karakrah – [LinkedIn](https://www.linkedin.com/in/bothaina-karakrah-57458219a/)

License: MIT