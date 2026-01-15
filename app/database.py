"""
Database connection and session management.
This file handles all SQLite database interactions.
"""

from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mortgage_applications.db")

# connect_args={"check_same_thread": False} is needed for SQLite
# to work with FastAPI's async nature
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to True to see SQL queries in console (For debugging)
    connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    """
    Creates all database tables defined in SQLModel.
    This should be called when the application starts.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency function that provides a database session.
    FastAPI will automatically handle opening and closing the session.
    
    Yields:
        Session: A SQLModel database session
    """
    with Session(engine) as session:
        yield session