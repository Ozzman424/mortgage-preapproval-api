# Mortgage Pre-Approval API

A backend API that simulates mortgage pre-approval decisions using debt-to-income ratios and credit score checks. I built this to combine my 5+ years of mortgage industry experience with my Python backend skills.

## 🎯 What It Does

This API evaluates loan applications using simple rules:
- Calculates your debt-to-income (DTI) ratio
- Checks if DTI is 45% or less
- Checks if credit score is 600 or higher
- Returns approved or declined with an explanation

## 🛠️ Tech Stack

- **FastAPI** - Web framework
- **SQLModel** - Database ORM
- **SQLite** - Database
- **Pydantic** - Data validation
- **pytest** - Testing

## 📁 Project Structure

```
mortgage-preapproval-api/
├── app/
│   ├── main.py          # API routes
│   ├── models.py        # Data models and business logic
│   ├── database.py      # Database setup
│   └── auth.py          # API key authentication
├── tests/
│   └── test_api.py      # Tests
├── .env                 # Environment variables
├── requirements.txt     # Dependencies
└── README.md           
```

## 🚀 Setup

### 1. Clone and Install

```bash
git clone https://github.com/Ozzman424/mortgage-preapproval-api.git
cd mortgage-preapproval-api

python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

### 2. Create .env File

```env
API_KEY=test_api_key_12345
DATABASE_URL=sqlite:///./mortgage_applications.db
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload
```

Go to: http://127.0.0.1:8000/docs

## 📡 API Endpoints

### GET /health
Check if API is running (no auth needed)

**Response:**
```json
{
  "status": "healthy",
  "message": "Mortgage Pre-Approval API is running"
}
```

### POST /simulate
Test approval without saving (needs API key)

**Request:**
```json
{
  "applicant_name": "John Doe",
  "monthly_income": 5000,
  "monthly_debts": 1500,
  "credit_score": 720,
  "loan_amount": 250000
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

### POST /applications
Save application to database (needs API key)

Same request format as `/simulate`, but saves to database and returns an ID.

### GET /applications/{id}
Get a saved application by ID

**Response:**
```json
{
  "id": 1,
  "applicant_name": "John Doe",
  "monthly_income": 5000.0,
  "credit_score": 720,
  "decision": "approved",
  "created_at": "2025-01-14T10:30:00"
}
```

## ⚙️ How to Use the API

### With cURL:

```bash
# Check health
curl http://127.0.0.1:8000/health

# Simulate approval
curl -X POST http://127.0.0.1:8000/simulate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test_api_key_12345" \
  -d '{"applicant_name":"John Doe","monthly_income":5000,"monthly_debts":1500,"credit_score":720,"loan_amount":250000}'
```

### With Browser:
Just go to http://127.0.0.1:8000/docs and use the interactive interface!

## 🧪 Running Tests

```bash
pytest tests/ -v
```

All 15 tests should pass.

## 🧠 How the Approval Logic Works

### DTI Calculation:
```
DTI = (Monthly Debts / Monthly Income) × 100
```

Example: $1,500 debts ÷ $5,000 income = 30% DTI

### Approval Rules:

| Rule | Result |
|------|--------|
| Credit score < 600 | ❌ Declined |
| DTI > 45% | ❌ Declined |
| Both pass | ✅ Approved |

## 📚 What I Learned

- Building REST APIs with FastAPI
- Using Pydantic for data validation
- Database operations with SQLModel
- Writing tests with pytest
- API authentication patterns
- Organizing a backend project

## 💡 Future Improvements

- Add PostgreSQL for production
- Implement JWT authentication
- Add more loan qualification rules (LTV, employment history)
- Deploy to cloud (Railway or Render)
