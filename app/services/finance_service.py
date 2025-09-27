from app.models.models import User, Transaction, Goal
from app.schemas.finance_schemas import UserCreate, TransactionCreate, GoalCreate
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy import func

# Secret key and algorithm for JWT encoding
SECRET_KEY = "supersecretkey"  # Use a secure key and store it in an environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to handle user signup (storing plain password)
def create_user(user: UserCreate, db: Session) -> User:
    # Use the plain password directly (no hashing)
    plain_password = user.password  # Storing plain password here (Not recommended)

    # Create a new User record in the database
    db_user = User(name=user.name, email=user.email, password_hash=plain_password)  # Store plain password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Function to create JWT token for the user after signup
def create_user_access_token(db_user: User) -> str:
    # Generate a JWT token
    access_token = create_access_token(data={"sub": db_user.email})
    return access_token

def create_transaction(user_id: int, transaction: TransactionCreate, db: Session) -> Transaction:
    db_transaction = Transaction(
        user_id=user_id,
        amount=transaction.amount,
        category=transaction.category,
        type=transaction.type,
        notes=transaction.notes,
        transaction_date=transaction.transaction_date
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def create_goal(user_id: int, goal: GoalCreate, db: Session) -> Goal:
    db_goal = Goal(
        user_id=user_id,
        target_amount=goal.target_amount,
        target_date=goal.target_date,
        # notes field may need to be added to your Goal model if not present
    )
    if hasattr(goal, "notes"):
        db_goal.notes = goal.notes
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_goals_with_progress(user_id: int, db: Session):
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    result = []
    for goal in goals:
        # Sum all 'Expense' transactions up to the goal's target_date
        progress = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == "Expense",
            Transaction.transaction_date <= goal.target_date
        ).scalar() or 0.0
        # If you want only 'Income' transactions, change type accordingly
        goal_data = {
            "goal_id": goal.goal_id,
            "target_amount": float(goal.target_amount),
            "target_date": goal.target_date,
            "notes": getattr(goal, "notes", None),
            "progress": float(progress)
        }
        result.append(goal_data)
    return result

