from .db import get_session
from sqlalchemy.orm import joinedload,Session
from sqlalchemy.exc import NoResultFound
from . import models
import datetime

def add_expense(session, user_id, wallet_id, category_id, amount, expense_date, note=None):
    # Nếu truyền string thì tự convert sang datetime.date
    if isinstance(expense_date, str):
        expense_date = datetime.datetime.strptime(expense_date, "%Y-%m-%d").date()
    
    wallet = update_wallet_balance(session,wallet_id,amount,models.EXPENSE)
    if(wallet == None): return
    
    expense = models.Expense(
        user_id=user_id,
        wallet_id=wallet_id,
        category_id=category_id,
        amount=amount,
        wallet_balance=wallet.balance, 
        expense_date=expense_date,
        note=note,
    )
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense

def list_expenses(session, user_id, month=None):
    query = session.query(models.Expense).filter(models.Expense.user_id == user_id)
    if month:
        query = query.filter(models.Expense.expense_date.like(f"{month}-%"))  # month="2025-09"
    results = query.options(joinedload(models.Expense.category)).all()
    session.close()
    return results

def add_income(session, user_id, wallet_id, category_id, amount, income_date, note=None):
    # Nếu truyền string thì tự convert sang datetime.date
    if isinstance(income_date, str):
        income_date = datetime.datetime.strptime(income_date, "%Y-%m-%d").date()

    wallet = update_wallet_balance(session,wallet_id,amount,models.INCOME)
    if(wallet == None): return
    
    income = models.Income(
        user_id=user_id,
        wallet_id=wallet_id,
        category_id=category_id,
        amount=amount,
        wallet_balance=wallet.balance, 
        income_date=income_date,
        note=note,
    )
    session.add(income)
    session.commit()
    session.refresh(income)
    return income

def list_incomes(session, user_id, month=None):
    query = session.query(models.Income).filter(models.Income.user_id == user_id)
    if month:
        query = query.filter(models.Income.income_date.like(f"{month}-%"))
    results = query.all()
    session.close()
    return results

def list_categories(session, user_id = 1,type = None):
    query = session.query(models.Category).filter(models.Category.user_id == user_id)
    if type:
        query = query.filter(models.Category.type == type)
    results = query.all()
    return results

def get_categories_list(session, user_id = 1, user_name = None ,type = None):
    
    # If user_name not None then find id match usser_name
    if user_name:
        user_id = get_user_id(session,user_name)
    
    # Get Category query result
    categories = list_categories(session,user_id,type)

    # Extract category name to list
    category_list:list = []
    for category in categories:
        category_list.append(category.category_name)

    return category_list


def update_wallet_balance(session: Session, wallet_id: int, amount: float, type:models.CategoryType) -> models.Wallet:
    """
    Cập nhật balance của ví.

    Args:
        session (Session): SQLAlchemy session.
        wallet_id (int): ID của ví cần cập nhật.
        amount (float): Số tiền thay đổi.
        is_income (bool): Nếu True thì cộng vào balance, nếu False thì trừ đi.

    Returns:
        Wallet: Object Wallet sau khi được update.
    """
    try:
        wallet = session.query(models.Wallet).filter(models.Wallet.wallet_id == wallet_id).one()
    except NoResultFound:
        raise ValueError(f"Wallet with id {wallet_id} not found")

    if type == models.INCOME:
        wallet.balance += amount
    elif type == models.EXPENSE:
        wallet.balance -= amount
    else :
        print("Invalid type")
        return None

    session.commit()
    session.refresh(wallet)  # refresh lại để lấy dữ liệu mới
    return wallet

def get_user_id(session: Session, user_name: str) -> int | None:
    """Truy xuất user_id từ username"""
    user = session.query(models.User).filter_by(username=user_name).first()
    return user.user_id if user else None

def get_category_id(session, user_name, category_name):
    user = session.query(models.User).filter_by(username=user_name).first()
    category = session.query(models.Category).filter_by(
        user_id=user.user_id,
        category_name=category_name
    ).first()
    return category.category_id if category else None
