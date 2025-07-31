# 🛡️ Fraud Detection System

A lightweight, real-time fraud detection API built with **FastAPI**, **async SQLAlchemy**, and a rule-based analysis engine. This project simulates financial transactions, detects suspicious activity, and provides fraud insights via a clean API and dashboard interface.

## 🚀 Features

- Asynchronous FastAPI backend
- Rule-based fraud detection logic.
- Live transaction analysis with fraud score & recommendation
- Alerts panel for high-risk activity
- Stats API for transaction/fraud overview
- Built-in support for PostgreSQL
- Realistic fake data generator included

---

## 🧰 Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pandas
---

## 📦 Installation

```bash
git clone https://github.com/Bothaina-Karakrah/fraud-detection-engine.git
cd fraud-detection-engine
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 🗃️ Environment Configuration

Create a `.env` file in the root:

```env
DATABASE_URL=postgresql+asyncpg://<user>:<password>@localhost/<dbname>
```

You can use `init_db.py` and `insert_sample_data.py` to set up tables and generate fake data.

---

## 🚦 Usage

### Run the API server:

```bash
uvicorn main:app --reload
```

### Run the FrontEnd:
```bash
# Navigate to frontend directory (e.g. dashboard)
cd dashboard

# Install dependencies
npm install

# Start the development server
npm run dev  # or npm start if you're using CRA
```

![img.png](img.png)

---

## 📊 Other Endpoints

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

Bothaina Karakrah – [LinkedIn](https://github.com/Bothaina-Karakrah)

License: MIT