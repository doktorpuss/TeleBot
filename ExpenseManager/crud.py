from ExpenseManager.db import get_session
from sqlalchemy.orm import joinedload,Session
from sqlalchemy.exc import NoResultFound
from ExpenseManager import models
from decimal import Decimal
import datetime

def add_expense(session, user_id, wallet_id, category_id, amount, expense_date, note=None):
    # Nếu amount là float thì convert sang Decimal
    if isinstance(amount, float):
        amount = Decimal(str(amount))  # tránh mất chính xác

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
    # Nếu amount là float thì convert sang Decimal
    if isinstance(amount, float):
        amount = Decimal(str(amount))  # tránh mất chính xác

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

def list_wallets(session, user_id = 1):
    query = session.query(models.Wallet).filter(models.Wallet.user_id == user_id)
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

def get_wallet_name(session, wallet_id: int) -> str | None:
    wallet = session.query(models.Wallet).filter(models.Wallet.wallet_id == wallet_id).first()
    return wallet.wallet_name if wallet else None

def get_wallet_id(session, user_id: int, wallet_name: str) -> int | None:
    wallet = session.query(models.Wallet).filter_by(
        user_id=user_id,
        wallet_name=wallet_name
    ).first()
    return wallet.wallet_id if wallet else None

def get_wallet_balance(session, wallet_id: int) -> float | None:
    wallet = session.query(models.Wallet).filter(models.Wallet.wallet_id == wallet_id).first()
    return float(wallet.balance) if wallet else None

def list_transactions(session, user_id, month=None):
    """
    Tổng hợp incomes + expenses trong 1 tháng (nếu có),
    sắp xếp theo ngày và trả về list các dict.
    """
    expenses = list_expenses(session, user_id, month)
    incomes = list_incomes(session, user_id, month)

    transactions = []

    # Convert expenses
    for e in expenses:
        transactions.append({
            "id": e.expense_id,
            "type": "expense",
            "amount": float(e.amount),
            "note": e.note,
            "date": e.expense_date,
            "wallet_id": e.wallet_id,
            "category_id": e.category_id,
            "category_name": e.category.category_name if hasattr(e, "category") else None
        })

    # Convert incomes
    for i in incomes:
        transactions.append({
            "id": i.income_id,
            "type": "income",
            "amount": float(i.amount),
            "note": i.note,
            "date": i.income_date,
            "wallet_id": i.wallet_id,
            "category_id": i.category_id
        })

    # Sort theo date
    transactions = sorted(transactions, key=lambda x: x["date"])

    return transactions