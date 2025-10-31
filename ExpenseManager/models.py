from sqlalchemy import Column, Integer, String, ForeignKey, Date, DECIMAL, Enum, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ExpenseManager.db import Base
import enum

EXPENSE = "Expense"
INCOME = "Income"

class CategoryType(enum.Enum):
    expense = "Expense"
    income = "Income"

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    user_tele_id = Column(String(255), nullable=False)
    email = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())

class Wallet(Base):
    __tablename__ = "wallets"
    wallet_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    wallet_name = Column(String(100), nullable=False)
    balance = Column(DECIMAL(15,2), default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    category_name = Column(String(100), nullable=False)
    type = Column(Enum(CategoryType), nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id",ondelete="CASCADE"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.wallet_id",ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id",ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(15,2), nullable=False)
    wallet_balance = Column(DECIMAL(15,2), nullable=False)
    transaction_date = Column(Date, nullable=False)
    note = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("Category", backref="transactions")
    wallet = relationship("Wallet", backref="transactions")

class Budget(Base):
    __tablename__ = "budgets"

    budget_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    budget_name = Column(String(100), nullable=False)   # ví dụ: "Chi tiêu thiết yếu tháng 10"
    balance = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Quan hệ
    user = relationship("User", backref="budgets")

class WishList(Base):
    __tablename__ = "wishlists"

    wish_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    wish_name = Column(String(100), nullable=False)
    cost = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Quan hệ
    user = relationship("User", backref="wishlists")
