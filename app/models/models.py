# app/models/models.py
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base

# ---------------------
# Users
# ---------------------
class User(Base):
    __tablename__ = "Users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # Add this line
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.getdate())

    # ORM relations (defined in child tables)
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user", cascade="save-update, merge"
    )
    goals: Mapped[list["Goal"]] = relationship(
        back_populates="user", cascade="save-update, merge"
    )

    def __repr__(self):
        return f"<User {self.user_id} {self.email}>"

# ---------------------
# Transactions
# ---------------------
class Transaction(Base):
    __tablename__ = "Transactions"
    __table_args__ = (
        # Add CHECK constraint for type column (Income or Expense)
        CheckConstraint("type IN ('Income', 'Expense')", name="ck_transactions_type"),
    )

    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("Users.user_id", name="fk_transactions_user_id"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # Income or Expense
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transaction_date: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.getdate())

    # Relationship with the User table
    user: Mapped[User] = relationship(back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.transaction_id} {self.type} {self.amount}>"

# ---------------------
# Goals
# ---------------------
class Goal(Base):
    __tablename__ = "Goals"

    goal_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("Users.user_id", name="fk_goals_user_id"),
        nullable=False,
        index=True,
    )
    target_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    target_date: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.getdate())

    # Relationship with the User table
    user: Mapped[User] = relationship(back_populates="goals")

    def __repr__(self):
        return f"<Goal {self.goal_id} {self.target_amount} by {self.target_date}>"
