"""
Unit tests for the Mortgage Pre-Approval API.
Tests both business logic and API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import calculate_dti, LoanApplicationRequest, evaluate_application
from app.database import create_db_and_tables
import os

os.environ["API_KEY"] = "test_api_key_12345"
os.environ["DATABASE_URL"] = "sqlite:///./test_mortgage.db"

create_db_and_tables()

client = TestClient(app)


# BUSINESS LOGIC TESTS

class TestDTICalculation:
    """Test the debt-to-income calculation logic"""
    
    def test_calculate_dti_basic(self):
        """Test basic DTI calculation"""
        # $1,500 debts / $5,000 income = 30%
        result = calculate_dti(monthly_debts=1500, monthly_income=5000)
        assert result == 30.0
    
    def test_calculate_dti_high(self):
        """Test high DTI calculation"""
        # $2,500 debts / $5,000 income = 50%
        result = calculate_dti(monthly_debts=2500, monthly_income=5000)
        assert result == 50.0
    
    def test_calculate_dti_low(self):
        """Test low DTI calculation"""
        # $500 debts / $5,000 income = 10%
        result = calculate_dti(monthly_debts=500, monthly_income=5000)
        assert result == 10.0
    
    def test_calculate_dti_zero_income_raises_error(self):
        """Test that zero income raises ValueError"""
        with pytest.raises(ValueError, match="Monthly income must be greater than zero"):
            calculate_dti(monthly_debts=1000, monthly_income=0)


class TestApplicationEvaluation:
    """Test the loan approval decision logic"""
    
    def test_approval_good_application(self):
        """Test that a good application gets approved"""
        app = LoanApplicationRequest(
            applicant_name="John Doe",
            monthly_income=5000,
            monthly_debts=1500,  # 30% DTI
            credit_score=720,
            loan_amount=250000
        )
        result = evaluate_application(app)
        assert result.decision == "approved"
        assert result.dti_ratio == 30.0
    
    def test_declined_low_credit_score(self):
        """Test that low credit score leads to decline"""
        app = LoanApplicationRequest(
            applicant_name="Jane Smith",
            monthly_income=5000,
            monthly_debts=1500,  # 30% DTI (good)
            credit_score=550,     # Below 600 threshold
            loan_amount=250000
        )
        result = evaluate_application(app)
        assert result.decision == "declined"
        assert "credit score" in result.message.lower()
    
    def test_declined_high_dti(self):
        """Test that high DTI leads to decline"""
        app = LoanApplicationRequest(
            applicant_name="Bob Johnson",
            monthly_income=5000,
            monthly_debts=2500,  # 50% DTI (too high)
            credit_score=720,    # Good credit
            loan_amount=250000
        )
        result = evaluate_application(app)
        assert result.decision == "declined"
        assert "debt-to-income" in result.message.lower()


# API ENDPOINT TESTS

class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check(self):
        """Test that health endpoint returns 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestSimulateEndpoint:
    """Test the /simulate endpoint"""
    
    def test_simulate_without_api_key(self):
        """Test that simulate requires API key"""
        response = client.post("/simulate", json={
            "applicant_name": "John Doe",
            "monthly_income": 5000,
            "monthly_debts": 1500,
            "credit_score": 720,
            "loan_amount": 250000
        })
        assert response.status_code == 403
    
    def test_simulate_approval_with_api_key(self):
        """Test successful approval simulation"""
        response = client.post(
            "/simulate",
            json={
                "applicant_name": "John Doe",
                "monthly_income": 5000,
                "monthly_debts": 1500,
                "credit_score": 720,
                "loan_amount": 250000
            },
            headers={"X-API-Key": "test_api_key_12345"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "approved"
        assert data["dti_ratio"] == 30.0
    
    def test_simulate_decline_low_credit(self):
        """Test decline due to low credit score"""
        response = client.post(
            "/simulate",
            json={
                "applicant_name": "Jane Smith",
                "monthly_income": 5000,
                "monthly_debts": 1500,
                "credit_score": 550,
                "loan_amount": 250000
            },
            headers={"X-API-Key": "test_api_key_12345"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "declined"
    
    def test_simulate_invalid_data(self):
        """Test validation error with invalid credit score"""
        response = client.post(
            "/simulate",
            json={
                "applicant_name": "Invalid User",
                "monthly_income": 5000,
                "monthly_debts": 1500,
                "credit_score": 900,  # Invalid: max is 850
                "loan_amount": 250000
            },
            headers={"X-API-Key": "test_api_key_12345"}
        )
        assert response.status_code == 422  # Validation error


class TestApplicationsEndpoint:
    """Test the /applications endpoint"""
    
    def test_create_application_without_api_key(self):
        """Test that creating application requires API key"""
        response = client.post("/applications", json={
            "applicant_name": "John Doe",
            "monthly_income": 5000,
            "monthly_debts": 1500,
            "credit_score": 720,
            "loan_amount": 250000
        })
        assert response.status_code == 403
    
    def test_create_and_retrieve_application(self):
        """Test creating and then retrieving an application"""
        # Create application
        create_response = client.post(
            "/applications",
            json={
                "applicant_name": "Test User",
                "monthly_income": 6000,
                "monthly_debts": 2000,
                "credit_score": 700,
                "loan_amount": 300000
            },
            headers={"X-API-Key": "test_api_key_12345"}
        )
        assert create_response.status_code == 201
        app_id = create_response.json()["id"]
        
        # Retrieve application
        get_response = client.get(f"/applications/{app_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["applicant_name"] == "Test User"
        assert data["decision"] in ["approved", "declined"]
    
    def test_get_nonexistent_application(self):
        """Test retrieving an application that doesn't exist"""
        response = client.get("/applications/99999")
        assert response.status_code == 404


# RUN TESTS

if __name__ == "__main__":
    pytest.main([__file__, "-v"])