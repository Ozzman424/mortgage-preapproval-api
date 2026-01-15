"""
Data models for the Mortgage Pre-Approval API.
These models define the structure of our data and validation rules.
"""

from sqlmodel import SQLModel, Field
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


# REQUEST MODEL - What the client sends to us

class LoanApplicationRequest(BaseModel):
    """
    Model for incoming loan application data.
    This is what the user sends when requesting a pre-approval simulation.
    """
    applicant_name: str = Field(..., min_length=2, max_length=100)
    monthly_income: float = Field(..., gt=0, description="Monthly gross income in dollars")
    monthly_debts: float = Field(..., ge=0, description="Total monthly debt payments")
    credit_score: int = Field(..., ge=300, le=850, description="FICO credit score")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    
    @field_validator('credit_score')
    @classmethod
    def validate_credit_score(cls, v):
        """Ensure credit score is in realistic range"""
        if v < 300 or v > 850:
            raise ValueError('Credit score must be between 300 and 850')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "applicant_name": "John Doe",
                "monthly_income": 5000.00,
                "monthly_debts": 1500.00,
                "credit_score": 720,
                "loan_amount": 250000.00
            }
        }
    }


# RESPONSE MODEL - What we send back to the client

class LoanDecisionResponse(BaseModel):
    """
    Model for the decision response we send back.
    Contains the approval/denial decision and explanation.
    """
    decision: str  # "approved" or "declined"
    message: str
    dti_ratio: float
    credit_score: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "decision": "approved",
                "message": "Applicant approved based on healthy DTI and credit score.",
                "dti_ratio": 30.0,
                "credit_score": 720
            }
        }
    }


# DATABASE MODEL - What we store in SQLite

class LoanApplication(SQLModel, table=True):
    """
    Database model for storing loan applications.
    SQLModel handles both Pydantic validation and SQLAlchemy ORM.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    applicant_name: str = Field(max_length=100)
    monthly_income: float
    monthly_debts: float
    credit_score: int
    loan_amount: float
    dti_ratio: float
    decision: str = Field(max_length=20)  # "approved" or "declined"
    decision_message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# BUSINESS LOGIC - The actual pre-approval calculation

def calculate_dti(monthly_debts: float, monthly_income: float) -> float:
    """
    Calculate Debt-to-Income ratio.
    
    DTI = (Total Monthly Debts / Gross Monthly Income) × 100
    
    Example: $1,500 in debts / $5,000 income = 0.30 = 30%
    
    Args:
        monthly_debts: Total monthly debt obligations
        monthly_income: Gross monthly income
        
    Returns:
        DTI as a percentage (e.g., 30.0 for 30%)
    """
    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than zero")
    
    dti = (monthly_debts / monthly_income) * 100
    return round(dti, 2)


def evaluate_application(application: LoanApplicationRequest) -> LoanDecisionResponse:
    """
    Main business logic: Evaluate if an applicant should be approved.
    
    Rules:
    1. DTI > 45% → DECLINED (too much debt relative to income)
    2. Credit Score < 600 → DECLINED (too risky)
    3. Otherwise → APPROVED
    
    Args:
        application: The loan application data
        
    Returns:
        LoanDecisionResponse with decision and explanation
    """
    # Step 1: Calculate DTI
    dti = calculate_dti(application.monthly_debts, application.monthly_income)
    
    # Step 2: Apply approval rules
    if application.credit_score < 600:
        return LoanDecisionResponse(
            decision="declined",
            message=f"Credit score of {application.credit_score} is below minimum requirement of 600.",
            dti_ratio=dti,
            credit_score=application.credit_score
        )
    
    if dti > 45:
        return LoanDecisionResponse(
            decision="declined",
            message=f"Debt-to-income ratio of {dti}% exceeds maximum of 45%.",
            dti_ratio=dti,
            credit_score=application.credit_score
        )
    
    return LoanDecisionResponse(
        decision="approved",
        message="Applicant approved based on healthy DTI and credit score.",
        dti_ratio=dti,
        credit_score=application.credit_score
    )