"""
Main FastAPI application with all endpoints.
This is the entry point for the Mortgage Pre-Approval API.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from contextlib import asynccontextmanager

# Import our custom modules
from app.models import (
    LoanApplicationRequest,
    LoanDecisionResponse,
    LoanApplication,
    evaluate_application
)
from app.database import create_db_and_tables, get_session, engine
from app.auth import verify_api_key



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This runs once when the application starts and cleans up on shutdown.
    Creates all database tables if they don't exist.
    """
    create_db_and_tables()
    yield


app = FastAPI(
    title="Mortgage Pre-Approval API",
    description="A simple API for mortgage pre-approval simulations and application storage",
    version="1.0.0",
    lifespan=lifespan
)



@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint - verifies the API is running.
    """
    return {
        "status": "healthy",
        "message": "Mortgage Pre-Approval API is running"
    }


@app.get("/applications/{application_id}", response_model=LoanApplication, tags=["Applications"])
def get_application(application_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a saved loan application by ID.
    
    Args:
        application_id: The ID of the application to retrieve
        session: Database session (automatically provided by FastAPI)
        
    Returns:
        The loan application if found
        
    Raises:
        404: If application not found
    """
    statement = select(LoanApplication).where(LoanApplication.id == application_id)
    application = session.exec(statement).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )
    
    return application



@app.post(
    "/simulate",
    response_model=LoanDecisionResponse,
    tags=["Simulation"],
    dependencies=[Depends(verify_api_key)]
)
def simulate_approval(application: LoanApplicationRequest):
    """
    Simulate a loan approval decision WITHOUT saving to database.
    
    This is useful for users who want to check their eligibility
    before formally applying.
    
    **Requires API Key in X-API-Key header**
    
    Business Rules:
    - DTI (Debt-to-Income) must be 45% or lower
    - Credit score must be 600 or higher
    
    Args:
        application: Loan application data
        
    Returns:
        Decision (approved/declined) with explanation
    """
    # Call our business logic function
    decision = evaluate_application(application)
    return decision


@app.post(
    "/applications",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    tags=["Applications"],
    dependencies=[Depends(verify_api_key)]
)
def create_application(
    application: LoanApplicationRequest,
    session: Session = Depends(get_session)
):
    """
    Submit and save a loan application to the database.
    
    This evaluates the application AND stores it for later retrieval.
    
    **Requires API Key in X-API-Key header**
    
    Args:
        application: Loan application data
        session: Database session (automatically provided)
        
    Returns:
        Application ID and decision
    """
    # Step 1: Evaluate the application using our business logic
    decision = evaluate_application(application)
    
    # Step 2: Create a database record
    db_application = LoanApplication(
        applicant_name=application.applicant_name,
        monthly_income=application.monthly_income,
        monthly_debts=application.monthly_debts,
        credit_score=application.credit_score,
        loan_amount=application.loan_amount,
        dti_ratio=decision.dti_ratio,
        decision=decision.decision,
        decision_message=decision.message
    )
    
    # Step 3: Save to database
    session.add(db_application)
    session.commit()
    session.refresh(db_application)  # Get the auto-generated ID
    
    # Step 4: Return the result
    return {
        "id": db_application.id,
        "decision": decision.decision,
        "message": decision.message,
        "dti_ratio": decision.dti_ratio,
        "created_at": db_application.created_at
    }



@app.get("/applications", response_model=List[LoanApplication], tags=["Applications"])
def list_applications(session: Session = Depends(get_session)):
    """
    List all loan applications (for demo/testing purposes).
    
    In a production system, you'd add pagination and filtering here.
    """
    statement = select(LoanApplication)
    applications = session.exec(statement).all()
    return applications