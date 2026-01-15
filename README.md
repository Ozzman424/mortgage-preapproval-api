# Mortgage Pre-Approval API

A lightweight Python backend API that simulates mortgage pre-approval decisions based on debt-to-income ratio and credit score. Built as a learning project to demonstrate backend development fundamentals.

## 🎯 What This Project Does

This API evaluates loan applications using simple financial rules:
- Calculates **Debt-to-Income (DTI)** ratio
- Checks if DTI ≤ 45%
- Verifies credit score ≥ 600
- Returns approval or denial with explanation

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **Pydantic/SQLModel** - Data validation and ORM
- **SQLite** - Lightweight database
- **pytest** - Testing framework
- **python-dotenv** - Environment configuration

## 📁 Project Structure

```
mortgage-preapproval-api/
├── app/
│   ├── main.py          # API routes and endpoints
│   ├── models.py        # Data models and business logic
│   ├── database.py      # Database configuration
│   └── auth.py          # API key authentication
├── tests/
│   └── test_api.py      # Unit tests
├── .env                 # Environment variables (create this)
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── ARCHITECTURE.md     # Technical design doc
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd mortgage-preapproval-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
API_KEY=your_secret_api_key_12345
DATABASE_URL=sqlite:///./mortgage_applications.db
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will start at `http://127.0.0.1:8000`

### 4. View API Documentation

Open your browser to:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 📡 API Endpoints

### Public Endpoints

#### `GET /health`
Health check to verify API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Mortgage Pre-Approval API is running"
}
```

#### `GET /applications/{id}`
Retrieve a saved loan application.

**Response:**
```json
{
  "id": 1,
  "applicant_name": "John Doe",
  "monthly_income": 5000.0,
  "monthly_debts": 1500.0,
  "credit_score": 720,
  "loan_amount": 250000.0,
  "dti_ratio": 30.0,
  "decision": "approved",
  "decision_message": "Applicant approved based on healthy DTI and credit score.",
  "created_at": "2025-01-14T10:30:00"
}
```

### Protected Endpoints (Require API Key)

Send API key in header: `X-API-Key: your_secret_api_key_12345`

#### `POST /simulate`
Simulate approval **without** saving to database.

**Request:**
```json
{
  "applicant_name": "John Doe",
  "monthly_income": 5000.00,
  "monthly_debts": 1500.00,
  "credit_score": 720,
  "loan_amount": 250000.00
}
```

**Response:**
```json
{
  "decision": "approved",
  "message": "Applicant approved based on healthy DTI and credit score.",
  "dti_ratio": 30.0,
  "credit_score": 720
}
```

#### `POST /applications`
Submit application and save to database.

**Request:** Same as `/simulate`

**Response:**
```json
{
  "id": 1,
  "decision": "approved",
  "message": "Applicant approved based on healthy DTI and credit score.",
  "dti_ratio": 30.0,
  "created_at": "2025-01-14T10:30:00"
}
```

## 🧪 Testing

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## 📝 Example Usage with cURL

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Simulate Approval
```bash
curl -X POST http://127.0.0.1:8000/simulate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_secret_api_key_12345" \
  -d '{
    "applicant_name": "John Doe",
    "monthly_income": 5000,
    "monthly_debts": 1500,
    "credit_score": 720,
    "loan_amount": 250000
  }'
```

### Submit Application
```bash
curl -X POST http://127.0.0.1:8000/applications \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_secret_api_key_12345" \
  -d '{
    "applicant_name": "Jane Smith",
    "monthly_income": 6000,
    "monthly_debts": 2000,
    "credit_score": 680,
    "loan_amount": 300000
  }'
```

### Get Application
```bash
curl http://127.0.0.1:8000/applications/1
```

## 🧠 Business Logic

### DTI Calculation
```
DTI = (Monthly Debts / Monthly Income) × 100
```

**Example:** $1,500 debts ÷ $5,000 income = 30% DTI

### Approval Rules

| Condition | Result |
|-----------|--------|
| Credit Score < 600 | ❌ Declined |
| DTI > 45% | ❌ Declined |
| Both conditions met | ✅ Approved |

## 📚 What I Learned

- Building RESTful APIs with FastAPI
- Data validation with Pydantic models
- Database operations with SQLModel/SQLAlchemy
- API authentication patterns
- Writing unit tests with pytest
- Structuring a Python backend project
- Environment configuration management

## 🔐 Security Notes

- API key authentication is basic; use OAuth2/JWT for production
- SQLite is development-only; use PostgreSQL/MySQL for production
- Add rate limiting for public APIs
- Implement proper error logging

## 📖 Additional Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical design.