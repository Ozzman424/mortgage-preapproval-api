# Architecture Documentation

## System Overview

The Mortgage Pre-Approval API is a three-tier application following REST principles:

```
Client Request → FastAPI Router → Business Logic → Database → Response
```

## Data Flow

### 1. Simulation Flow (`POST /simulate`)

```
1. Client sends loan data with API key
2. FastAPI validates API key (auth.py)
3. Pydantic validates request data (models.py)
4. evaluate_application() calculates DTI and applies rules
5. Return decision JSON (no database interaction)
```

### 2. Application Creation Flow (`POST /applications`)

```
1. Client sends loan data with API key
2. API key validation
3. Request data validation
4. evaluate_application() makes decision
5. Create LoanApplication database record
6. Save to SQLite via SQLModel
7. Return decision + application ID
```

### 3. Application Retrieval Flow (`GET /applications/{id}`)

```
1. Client requests application by ID
2. Query SQLite database
3. Return application if found, else 404
```

## Component Breakdown

### `app/main.py` - API Layer
**Responsibility:** HTTP request/response handling

- Defines API endpoints
- Manages routing
- Handles dependencies (DB sessions, auth)
- Returns appropriate HTTP status codes

**Key Design Pattern:** Dependency Injection
- `session: Session = Depends(get_session)` - Auto-manages DB connections
- `dependencies=[Depends(verify_api_key)]` - Protects endpoints

### `app/models.py` - Business Logic & Data Models
**Responsibility:** Data validation and business rules

**Three model types:**
1. **LoanApplicationRequest** (Pydantic BaseModel)
   - Validates incoming API requests
   - Enforces constraints (credit score 300-850, positive income)
   
2. **LoanDecisionResponse** (Pydantic BaseModel)
   - Structures API responses
   - Ensures consistent output format

3. **LoanApplication** (SQLModel, table=True)
   - Maps to SQLite table
   - Handles database persistence
   - Auto-generates ID and timestamp

**Business Logic Functions:**
- `calculate_dti()` - Pure calculation, no side effects
- `evaluate_application()` - Decision logic isolated from API layer

**Why separate?** Allows testing business logic without HTTP layer.

### `app/database.py` - Data Access Layer
**Responsibility:** Database connection management

- Creates SQLite engine
- Provides session factory via `get_session()`
- Initializes tables on startup

**Key Pattern:** Context Manager
```python
with Session(engine) as session:
    yield session
```
Ensures connections always close properly.

### `app/auth.py` - Security Layer
**Responsibility:** API authentication

- Loads secret key from environment
- Validates `X-API-Key` header
- Returns 403 if invalid/missing

**Design Choice:** Header-based (not query parameter)
- Prevents keys in logs/URLs
- Industry standard for API keys

## Database Schema

### `loan_applications` Table

| Column | Type | Constraints |
|--------|------|------------|
| id | INTEGER | Primary Key, Auto-increment |
| applicant_name | VARCHAR(100) | Not Null |
| monthly_income | FLOAT | Not Null |
| monthly_debts | FLOAT | Not Null |
| credit_score | INTEGER | Not Null |
| loan_amount | FLOAT | Not Null |
| dti_ratio | FLOAT | Not Null |
| decision | VARCHAR(20) | Not Null |
| decision_message | TEXT | Not Null |
| created_at | DATETIME | Default: UTC Now |

**Indexes:** Primary key on `id` (automatic)

**Why SQLite?**
- Zero-config development
- File-based (portable)
- Sufficient for 100K+ records
- Production would use PostgreSQL

**Security Limitations:**
- Static key (not token-based)
- No expiration
- No user roles
- Production needs OAuth2/JWT

## Error Handling Strategy

### Validation Errors (422)
Pydantic automatically validates:
- Credit score 300-850
- Positive income
- Required fields present

### Not Found (404)
Custom handling in `get_application()`:
```python
if not application:
    raise HTTPException(status_code=404)
```

### Forbidden (403)
Auth layer handles invalid API keys

### Database Errors
SQLModel/SQLAlchemy catch connection issues

## Testing Architecture

### Unit Tests (`test_api.py`)

**Three test categories:**

1. **Business Logic Tests**
   - Test pure functions (calculate_dti)
   - No HTTP or database needed
   - Fast execution

2. **API Endpoint Tests**
   - Uses TestClient (doesn't require running server)
   - Tests HTTP request/response
   - Verifies status codes

3. **Integration Tests**
   - Tests full flow: API → Logic → Database
   - Uses in-memory SQLite

**Test Isolation:**
Each test uses separate database session - no shared state.

## Scalability Considerations

### Current Limitations
- Single-threaded SQLite
- Static API key (can't revoke)
- No caching
- No pagination on list endpoint

## Design Principles Applied

### Separation of Concerns
Each file has single responsibility:
- `main.py` - HTTP handling
- `models.py` - Data & logic
- `database.py` - Data access
- `auth.py` - Security

### Dependency Injection
FastAPI manages:
- Database sessions (auto-commit/rollback)
- Authentication checks
- Request validation

### Fail-Fast Validation
Pydantic validates at API boundary before business logic runs.

### Testability
Business logic is pure functions - easy to test without mocking.

## Future Enhancements

1. **Additional Rules:**
   - Loan-to-value ratio
   - Employment history check
   - Property appraisal

2. **Features:**
   - Email notifications
   - Document upload (PDF bank statements)
   - Multi-step application workflow

3. **Architecture:**
   - Microservices (separate credit check service)
   - Event-driven (publish approval events)
   - API versioning (/v1/simulate)