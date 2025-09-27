from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# For local SQL Server Express with Windows Authentication
DATABASE_URL = (
    "mssql+pyodbc://@PRAJOTH\\SQLEXPRESS/PersonalFinanceTracker"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for models
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
