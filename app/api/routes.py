# app/api/routes.py
from fastapi import APIRouter, HTTPException, Depends, status, Header, Query
from sqlalchemy.orm import Session
from app.models import models
from app.schemas.finance_schemas import UserCreate, UserOut, TransactionCreate, GoalCreate, GoalOut
from app.services import finance_service
from app.database import get_db
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from app.models.models import User
from app.services.finance_service import SECRET_KEY, ALGORITHM
from app.schemas.finance_schemas import TransactionOut
from typing import List
from datetime import date
from sqlalchemy import func

router = APIRouter()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Signup Route - This will handle user registration
@router.post("/signup", response_model=UserOut, status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create the new user using the service
    new_user = finance_service.create_user(user, db)

    # Create JWT token for the new user
    access_token = finance_service.create_user_access_token(db_user=new_user)

    return UserOut(user_id=new_user.user_id, name=new_user.name, email=new_user.email)

# Login Route - This will handle user authentication
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or db_user.password_hash != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    access_token = finance_service.create_user_access_token(db_user=db_user)
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Header(..., alias="Authorization"), db: Session = Depends(get_db)) -> User:
    try:
        scheme, _, param = token.partition(" ")
        payload = jwt.decode(param if scheme == "Bearer" else token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



@router.post("/transactions", status_code=201)
def add_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_transaction = finance_service.create_transaction(current_user.user_id, transaction, db)
    return {
        "transaction_id": new_transaction.transaction_id,
        "amount": new_transaction.amount,
        "category": new_transaction.category,
        "type": new_transaction.type,
        "notes": new_transaction.notes,
        "transaction_date": str(new_transaction.transaction_date)
    }

@router.get("/transactions", response_model=List[TransactionOut])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    transaction_date: date = Query(None, description="Filter by transaction date (YYYY-MM-DD)")
):
    try:
        query = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.user_id
        )
        if transaction_date:
            query = query.filter(models.Transaction.transaction_date == transaction_date)
        transactions = query.order_by(models.Transaction.transaction_date.desc()).all()
        return transactions
    except Exception as e:
        print("Error in get_transactions:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/goals", response_model=GoalOut, status_code=201)
def add_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_goal = finance_service.create_goal(current_user.user_id, goal, db)
    # Calculate progress for the new goal
    progress = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.user_id == current_user.user_id,
        models.Transaction.type == "Expense",
        models.Transaction.transaction_date <= new_goal.target_date
    ).scalar() or 0.0
    return GoalOut(
        goal_id=new_goal.goal_id,
        target_amount=float(new_goal.target_amount),
        target_date=new_goal.target_date,
        notes=getattr(new_goal, "notes", None),
        progress=float(progress)
    )

@router.get("/goals", response_model=List[GoalOut])
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goals = finance_service.get_goals_with_progress(current_user.user_id, db)
    return goals
