from ExpenseManager import crud
from ExpenseManager.db import get_session,init_db
from ExpenseManager.TeleBotFinManUtil import make_type_pie_chart,make_category_pie_chart,make_history_table, make_monthly_report
from colorama import Fore,Style
import pandas as pd

# ====== Tạo db (chỉ cần làm khi chưa có db) ======
# init_db()

# ================= Lấy session ===================
session = get_session()

# # ================= Thêm expense ==================
# expense = crud.add_expense(
#     session,
#     user_id=1,
#     wallet_id=1,
#     category_id=2,
#     amount=70000,
#     expense_date="2025-10-5",
#     note="Ăn trưa"
# )
# print("Đã thêm:", expense.expense_id)

# # ================= Thêm income ==================
# income = crud.add_income(
#     session,
#     user_id=1,
#     wallet_id=1,
#     category_id=9,
#     amount=70000,
#     income_date="2025-10-2",
#     note="Test"
# )
# print("Đã thêm:", income.income_id)

# ======= Lấy danh sách chi tiêu theo tháng ======= 
expenses = crud.list_expenses(session=session,user_id=1, month="2025-9")
print(Fore.RED)
for e in expenses:
    print(e.expense_date, e.amount, e.category.category_name,e.note, )
print(Fore.WHITE)
    

# ========== Tìm user_id theo user_name ===========
user_name = "Quang"
uid = crud.get_user_id(session=session, user_name=user_name)
print(Fore.GREEN)
print(f"User: {user_name} \t UID: {uid}")
print(Fore.WHITE)


# ====== Tìm category_id theo category_name =======
user_name = "Quang"
category_name = "Đi lại"
category_id = crud.get_category_id(session=session, user_name=user_name, category_name=category_name)                    
print(Fore.LIGHTCYAN_EX)
print(f"User: {user_name} \t Category: {category_name} \t Category ID: {category_id}")
print(Fore.WHITE)

# ========== Liệt kê danh sách category ===========
user_name = "Quang"
income_categories = crud.get_categories_list(session=session, user_name=user_name, type=crud.models.EXPENSE)
print(Fore.RED)
print(income_categories)
print(Fore.WHITE)

# ===== Vẽ bảng liệt kê lịch sử giao dịch trong tháng =====
# transactions = crud.list_transactions(session,1,"2025-10")
# dt = pd.DataFrame(transactions)
# table = make_history_table(dt)
# print("Table created at:", table)


# ===== Vẽ biểu đồ cơ cấu giao dịch trong tháng =====
# transactions = crud.list_transactions(session,1,"2025-10")
# dt = pd.DataFrame(transactions)
# report = make_type_pie_chart(dt,"expense")
# # report = make_category_pie_chart(dt,"🍔 Ăn uống")
# print("Report created at:", report)

# ============= Tạo báo cáo chi tiêu tháng =============
report = make_monthly_report("2025-09","Quang")
print("Report created at:", report)

# ['💵 Lương', '💸 Thưởng', '📈 Đầu tư', '💼 Kinh doanh', 'Khác']
# ['🍔 Ăn uống', '🏍  Đi lại', '🏠 Nhà ở', '🎮 Giải trí', '🛒 Mua sắm', '💊 Sức khỏe', '📖 Giáo dục', 'Khác']