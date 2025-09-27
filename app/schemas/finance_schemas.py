# app/schemas/schemas.py
from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr


# Schema for creating a new user (Signup)
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str  # User's password for signup

    class Config:
        orm_mode = True  # This allows Pydantic to read data from SQLAlchemy models

# Schema for displaying a user's data (optional, used for GET requests)
class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True  # This allows Pydantic to read data from SQLAlchemy models

class TransactionCreate(BaseModel):
    amount: float
    category: str
    type: str  # "Income" or "Expense"
    notes: str | None = None
    transaction_date: str  # ISO date string

    class Config:
        orm_mode = True

class TransactionOut(BaseModel):
    transaction_id: int
    amount: float
    category: str
    type: str
    notes: Optional[str] = None
    transaction_date: date  # <-- Change from str to date

    class Config:
        orm_mode = True

class GoalCreate(BaseModel):
    target_amount: float
    target_date: date
    notes: Optional[str] = None

    class Config:
        orm_mode = True

class GoalOut(BaseModel):
    goal_id: int
    target_amount: float
    target_date: date
    notes: Optional[str] = None
    progress: float  # Amount saved towards the goal

    class Config:
        orm_mode = True
