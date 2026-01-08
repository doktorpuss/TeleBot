from ExpenseManager.db import get_session
from sqlalchemy.orm import joinedload,Session
from sqlalchemy.exc import NoResultFound
from ExpenseManager import models
from decimal import Decimal
from colorama import Fore,Back,Style
import datetime

session = get_session()
# TRANSACTION
# region 
def add_transaction(session, user_id, wallet_id, category_id, amount,transaction_date, type, note=None):
    # Nếu amount là float thì convert sang Decimal
    if isinstance(amount, float):
        amount = Decimal(str(amount))  # tránh mất chính xác

    # Nếu truyền string thì tự convert sang datetime.date
    if isinstance(transaction_date, str):
        transaction_date = datetime.datetime.strptime(transaction_date, "%Y-%m-%d").date()

    wallet = update_wallet_balance(session,wallet_id,amount,type)
    if(wallet == None): return
    
    transaction = models.Transaction(
        user_id=user_id,
        wallet_id=wallet_id,
        category_id=category_id,
        amount=amount,
        wallet_balance=wallet.balance, 
        transaction_date=transaction_date,
        note=note,
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

def list_transactions(session, user_id, month=None):
    query = session.query(models.Transaction).filter(models.Transaction.user_id == user_id)
    if month:
        query = query.filter(models.Transaction.transaction_date.like(f"{month}-%"))
    results = query.options(
        joinedload(models.Transaction.wallet),
        joinedload(models.Transaction.category)
    ).all()

    transactions = []
    for i in results:
        transactions.append({
            "id": i.transaction_id,
            "type": i.category.type if i.category else "Missing",
            "amount": i.amount,
            "date": i.transaction_date,
            "note": i.note,
            "category": i.category.category_name if i.category else "Missing",
            "wallet": i.wallet.wallet_name if i.wallet else "Missing",
            "wallet_balance": i.wallet_balance
        })
    return transactions
#endregion

# USER
# region
def get_user_id(session: Session, user_name: str) -> int | None:
    """Truy xuất user_id từ username"""
    user = session.query(models.User).filter_by(username=user_name).first()
    return user.user_id if user else None

def get_user_info(session: Session = session, user_id: int = None, user_name: str = None, user_tele_id = None) -> models.User | None:
    query = session.query(models.User)
    filters = []

    if user_id is not None:
        filters.append(models.User.user_id == user_id)
    if user_name is not None:
        filters.append(models.User.username == user_name)
    if user_tele_id is not None:
        filters.append(models.User.user_tele_id == user_tele_id)

    if not filters:
        return None  # không có tiêu chí nào -> không query

    users = query.filter(*filters).first()
    return users

def add_user(session: Session, user_name: str, user_tele_id: str, email: str = None) -> models.User:

    user = models.User(
        username=user_name,
        user_tele_id=user_tele_id,
        email = email,
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# endregion

# CATEGORY
# region 
def get_categories_list(session = session, user_id = None, type = None):
    # Get Category query result
    categories = get_category_info(user_id = user_id, type = type)

    if not categories:
        return "No category found"

    # Extract category name to list
    category_list:list = []
    for category in categories:
        category_list.append(category.category_name)

    return category_list

def get_category_info(
    session = session,
    category_id: int = None,
    user_id: int = None,
    category_name: str = None,
    type: models.CategoryType = None
) -> list[models.Category] | None:

    query = session.query(models.Category)
    filters = []

    if category_id is not None:
        filters.append(models.Category.category_id == category_id)
    if user_id is not None:
        filters.append(models.Category.user_id == user_id)
    if category_name is not None:
        filters.append(models.Category.category_name == category_name)
    if type is not None:
        filters.append(models.Category.type == type)

    if not filters:
        return None  # không có tiêu chí nào -> không query

    categories = query.filter(*filters).all()
    return categories

def add_new_category(session = session, user_id: int = None, category_name: str = None, type: models.CategoryType = None) -> models.Category:
    
    if not user_id:
        print(Fore.RED + "Create new category failed: User id not provided" + Style.RESET_ALL)
        raise ValueError("Không xác định được người dùng")
    if not category_name:
        print(Fore.RED + "Create new category failed: Category name not provided" + Style.RESET_ALL)
        raise ValueError("Tên danh mục không hợp lệ")
    if not type:
        print(Fore.RED + "Create new category failed: Category type not provided" + Style.RESET_ALL)
        raise ValueError("Không xác định loại danh mục")
    
    category = models.Category(
        user_id=user_id,
        category_name=category_name,
        type=type
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

# endregion

# WALLET
# region
def update_wallet_balance(session: Session, wallet_id: int, amount: float, type:models.CategoryType) -> models.Wallet:
   
    try:
        wallet = session.query(models.Wallet).filter(models.Wallet.wallet_id == wallet_id).one()
    except NoResultFound:
        raise ValueError(f"Wallet with id {wallet_id} not found")

    # 🔹 Ép kiểu amount sang Decimal để tránh lỗi cộng trừ
    if isinstance(amount, float):
        amount = Decimal(str(amount))

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

def get_wallet_info(session = session, wallet_id: int = None, user_id: int =None) -> models.Wallet | None:
    query = session.query(models.Wallet)
    filters = []

    if wallet_id is not None:
        filters.append(models.Wallet.wallet_id == wallet_id)
    if user_id is not None: 
        filters.append(models.Wallet.user_id == user_id)

    if not filters:
        return None  # không có tiêu chí nào -> không query

    wallets = query.filter(*filters).all()
    return wallets

def add_new_wallet(session = session, user_id = None, wallet_name = None):

    if not user_id:
        print(Fore.RED + "Create new wallet failed: User id not provided" + Style.RESET_ALL)
        return None

    if not wallet_name:
        print(Fore.RED + "Create new wallet failed: Wallet name not provided" + Style.RESET_ALL)
        return None

    wallet = models.Wallet(
        user_id = user_id,
        wallet_name = wallet_name,
        balance = 0
    )
    session.add(wallet)
    session.commit()
    session.refresh(wallet)
    return wallet
# endregion

# BUDGET
# region
def update_budget_balance(budget_id = None, session = session, amount = None, is_spending: bool = False):
    try:
        budget = session.query(models.Budget).filter(models.Budget.budget_id == budget_id).one()
    except NoResultFound:
        raise ValueError(f"Budget with id {budget_id} not found")
    
    # 🔹 Ép kiểu amount sang Decimal để tránh lỗi cộng trừ
    if isinstance(amount, float):
        amount = Decimal(str(amount))
    
    if is_spending:
        budget.balance -= amount
    else:
        budget.balance += amount

    session.commit()
    session.refresh(budget)
    return budget

def get_budget_info(session = session, budget_id: int = None, user_id: int = None) -> models.Budget | None:
    if budget_id:
        return session.query(models.Budget).filter(models.Budget.budget_id == budget_id).first()
    if user_id:
        return session.query(models.Budget).filter(models.Budget.user_id == user_id).all()
    return None

def add_new_budget(session = session, user_id = None, budget_name = ""):
    if not user_id:
        print(Fore.RED + "Create new budget failed: User id not provided" + Style.RESET_ALL)
        return None

    if not budget_name:
        print(Fore.RED + "Create new budget failed: Budget name not provided" + Style.RESET_ALL)
        return None

    budget = models.Budget(
        user_id=user_id,
        budget_name=budget_name,
        balance=0
    )
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget

# endregion

# WISHLIST
# region
def get_wishlist(session = session, user_id = None):
    if user_id:
        return session.query(models.WishList).filter(models.WishList.user_id == user_id).all()
    return None

def add_wishlist(session = session, user_id = None, cost = None, wishlist_name = ""):
    if not user_id:
        print(Fore.RED + "Create new whislist failed: User id not provided" + Style.RESET_ALL)
        return None

    if not wishlist_name:
        print(Fore.RED + "Create new whislist failed: WishList name not provided" + Style.RESET_ALL)
        return None
    
    if not cost:
        print(Fore.RED + "Create new whislist failed: Cost not provided" + Style.RESET_ALL)
        return None
    

    whislist = models.WishList(
        user_id=user_id,
        wish_name=wishlist_name,
        cost = cost
    )
    session.add(whislist)
    session.commit()
    session.refresh(whislist)
    return whislist

def execute_wishlist(session = session, wishlist_id = None):
    if wishlist_id:
        session.query(models.WishList).filter(models.WishList.wish_id == wishlist_id).delete()
        session.commit()
        return True
    return False
# endregion