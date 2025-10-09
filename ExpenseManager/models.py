from sqlalchemy import Column, Integer, String, ForeignKey, Date, DECIMAL, Enum, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ExpenseManager.db import Base
import enum

'''
1|1|Ăn uống|expense
2|1|Đi lại|expense
3|1|Nhà ở|expense
4|1|Giải trí|expense
5|1|Mua sắm|expense
6|1|Sức khỏe|expense
7|1|Giáo dục|expense
8|1|Khác|expense
9|1|Lương|income
10|1|Thưởng|income
11|1|Đầu tư|income
12|1|Kinh doanh|income
13|1|Khác|income
'''

EXPENSE = "expense"
INCOME = "income"

class CategoryType(enum.Enum):
    expense = "expense"
    income = "income"

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
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
    budget_id = Column(Integer, ForeignKey("budgets.budget_id"), nullable=True)

    budget = relationship("Budget", back_populates="categories")

class Expense(Base):
    __tablename__ = "expenses"
    expense_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.wallet_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    amount = Column(DECIMAL(15,2), nullable=False)
    wallet_balance = Column(DECIMAL(15,2), nullable=False)
    expense_date = Column(Date, nullable=False)
    note = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("Category", backref="expenses")
    wallet = relationship("Wallet", backref="expenses")

class Income(Base):
    __tablename__ = "incomes"
    income_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.wallet_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    amount = Column(DECIMAL(15,2), nullable=False)
    wallet_balance = Column(DECIMAL(15,2), nullable=False)
    income_date = Column(Date, nullable=False)
    note = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("Category", backref="incomes")
    wallet = relationship("Wallet", backref="incomes")

class Budget(Base):
    __tablename__ = "budgets"

    budget_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    budget_name = Column(String(100), nullable=False)   # ví dụ: "Chi tiêu thiết yếu tháng 10"
    balance = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Quan hệ
    user = relationship("User", backref="budgets")
    categories = relationship("Category", back_populates="budget")
