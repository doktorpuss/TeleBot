from ExpenseManager import crud,db,models
import datetime
from colorama import Fore,Back,Style
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler,CommandHandler,MessageHandler,filters,ContextTypes,ConversationHandler

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

# utilities
# region
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
session = db.get_session()

currency = "VND"

def get_created_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_this_month():
    return datetime.datetime.now().strftime("%Y-%m")

def normalize_date_string(date_str: str) -> str:
    """
    Chuẩn hóa chuỗi ngày về dạng ISO `YYYY-MM-DD`
    - Nếu input đã là ISO thì trả nguyên.
    - Nếu input là dd/mm/yyyy thì đổi sang yyyy-mm-dd.
    """
    try:
        # Trường hợp đã là ISO
        print("kiểm tra ISO : ", date_str)
        datetime.datetime.fromisoformat(date_str)
        # print("ISO")
        return date_str
    except ValueError:
        pass

    # Trường hợp dd/mm/yyyy
    if "/" in date_str:
        # print("dd/mm/yyyy")
        try:
            day, month, year = date_str.split("/")
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except Exception:
            return "Date unrecognized"

    return "Date unrecognized"

# =================== CHECK USER VALIDATION ===================
def is_user_valid(user_tele_id):
    user = crud.get_user_info(session = session, user_tele_id = user_tele_id)[0]

    if user is None:
        return False
    
    return True
# endregion

# REGISTRATION
# region
# =================== REGISTRATION FOR NEW USER ===============
registration_allowed = False
async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.name
    user_tele_id = update.message.from_user.id 
    print(Fore.MAGENTA)
    print("New user requested:")

    if registration_allowed:
        new_user = crud.add_user(session = session, user_name=user_name, user_tele_id=user_tele_id)
        print(Fore.LIGHTGREEN_EX)
        print("------------------------------")
        print("User registered successfully:")
        print("User id:", new_user.user_id)
        print("User name:", new_user.username)
        print("User tele_id:", new_user.user_tele_id)
        print("------------------------------")

        await update.message.reply_text("✅ Đăng ký người dùng thành công")
    else:
        print(Fore.LIGHTRED_EX)
        print("Registration not allowed")
        await update.message.reply_text("⚠️ Đăng ký người dùng không thành công")
    print(Style.RESET_ALL)

async def registration_allow_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.name
    print(Fore.LIGHTGREEN_EX + f"User: {user_name}" + Style.RESET_ALL)
    user_tele_id = update.message.from_user.id
    print(Fore.LIGHTRED_EX + f"ID: {user_tele_id}" + Style.RESET_ALL)

    if not is_user_valid(user_tele_id):
        print(Fore.LIGHTRED_EX + f"User: {user_name}| REJECTED: database unknown" + Style.RESET_ALL)
        await update.message.reply_text("⚠️ Người dùng không hợp lệ.")
        return ConversationHandler.END

    admin = crud.get_user_info(user_id = 1)[0]

    print(admin.username)
    print(admin.user_tele_id)
    if (
    user_name is None or
    user_name.strip().lower() != (admin.username or '').strip().lower() or
    int(user_tele_id) != int(admin.user_tele_id)
    ):
        print("Not admin, cannot allow registration")
        await update.message.reply_text("⚠️ Only admin can allow registration")
        return
    else:
        global registration_allowed
        registration_allowed = not registration_allowed

    if registration_allowed:
        await update.message.reply_text("🟢 Bật chế độ đăng ký mới")
    else:
        await update.message.reply_text("🔴 Tắt chế độ đăng ký mới")

    print("Registration allowed:", registration_allowed) 

# endregion

# TRANSACTION
# region

# =================== ADD TRANSACTION CONVERSATION ===================
ASK_TRANSACTION_TYPE = "ASK_TRANSACTION_TYPE"
ASK_AMOUNT = "ASK_AMOUNT"
ASK_CATEGORY = "ASK_CATEGORY"
ASK_DATE = "ASK_DATE"
ASK_DATE_OTHER = "ASK_DATE_OTHER"
ASK_WALLET = "ASK_WALLET"
ASK_TRANSACTION_BUDGET = "ASK_TRANSACTION_BUDGET"
ASK_NOTE = "ASK_NOTE"
ADD_INCOME = "ADD_INCOME"
CONFIRM = "CONFIRM"


async def ask_transaction_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    user_tele_id = update.message.from_user.id

    print(Fore.MAGENTA + f"USER {user_tele_id} TRY ADD TRANSACTION" + Style.RESET_ALL)

    user = crud.get_user_info(session=session,user_tele_id=user_tele_id)[0]
    if not user:
        print(Fore.LIGHTRED_EX + f"User: {user_tele_id}| REJECTED: database unknown" + Style.RESET_ALL)
        await update.message.reply_text("⚠️ Người dùng không hợp lệ.")
        context.user_data.clear()
        return ConversationHandler.END
    
    context.user_data['transaction'] = {
        'type': None,
        'date': None,
        'amount': 0.0,
        'category_id': None,
        'category_name': None,
        'wallet_id': None,
        'wallet_name': None,
        'budget_id': None,
        'budget_name': None,
        'user_id': user.user_id,
        'note': None
    }

    keyboard = [[InlineKeyboardButton("Chi tiêu", callback_data=models.EXPENSE),
                InlineKeyboardButton("Thu nhập", callback_data=models.INCOME)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Vui lòng chọn loại giao dịch", reply_markup=reply_markup)

    return ASK_TRANSACTION_TYPE

async def ask_transaction_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.callback_query.answer()

    context.user_data['transaction']['type'] = update.callback_query.data
    
    await update.callback_query.message.reply_text("Nhập số tiền thu nhập:")
    return ASK_AMOUNT

async def ask_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    try:
        context.user_data['transaction']['amount'] = float(update.message.text)

        # Get category list depend on type
        categories: models.Category = crud.get_category_info(
            user_id = context.user_data['transaction']['user_id'],
            type = models.CategoryType(context.user_data['transaction']['type'])
            )
        if categories == []:
            await update.message.reply_text("Bạn chưa có danh mục chi tiêu nào, hãy tạo danh mục mới với /create_category")
            context.user_data.clear()
            return ConversationHandler.END

        # print("Categories:", categories)
        #make inline keyboard from categories by vertical list
        keyboard = []
        for category in categories:
            keyboard.append([InlineKeyboardButton(f"{category.category_name}", callback_data=f"{category.category_id}|{category.category_name}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        #Send request
        await update.message.reply_text("Chọn danh mục thu nhập:", reply_markup=reply_markup)
        return ASK_CATEGORY
    
    except ValueError:
        await update.message.reply_text("Số tiền không hợp lệ. Vui lòng nhập lại số tiền thu nhập:")
        return ASK_AMOUNT

async def ask_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()

    context.user_data['transaction']['category_id'] = query.data.split("|")[0]
    context.user_data['transaction']['category_name'] = query.data.split("|")[1]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hôm nay", callback_data="today")],
                    [InlineKeyboardButton("Hôm qua", callback_data="day_before")],
                    [InlineKeyboardButton("Ngày khác", callback_data="other")]])
    
    await query.edit_message_text(f"danh mục [{context.user_data['transaction']['category_name']}] \nNgày giao dịch:",reply_markup=reply_markup)
    return ASK_DATE

async def ask_date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()

    if query.data == "today":
        date_str = datetime.date.today().isoformat().__str__().split()[0]
    elif query.data == "day_before":
        date_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat().__str__().split()[0]
    elif query.data == "other":
        await query.edit_message_text("Vui lòng nhập ngày giao dịch (YYYY-MM-DD hoặc DD/MM/YYYY):")
        return ASK_DATE_OTHER
    
    context.user_data['transaction']['date'] = date_str

    # Get wallet list
    wallets = crud.get_wallet_info(user_id=context.user_data['transaction']['user_id'])

    # Make inline keyboard from wallets by vertical list
    keyboard = []
    for wallet in wallets:
        keyboard.append([InlineKeyboardButton(f"{wallet.wallet_name}: {wallet.balance:,.0f} {currency}", callback_data=f"{wallet.wallet_id}|{wallet.wallet_name}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send request
    await query.edit_message_text("Chọn ví giao dịch:", reply_markup=reply_markup)
    return ASK_WALLET

async def ask_date_other_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    date_str = normalize_date_string(update.message.text)

    if date_str == "Date unrecognized":
        await update.message.reply_text("Ngày không hợp lệ. Vui lòng nhập lại ngày giao dịch (YYYY-MM-DD hoặc DD/MM/YYYY):")
        return ASK_DATE
    
    context.user_data['transaction']['date'] = date_str

    # Get wallet list
    wallets = crud.get_wallet_info(user_id=context.user_data['transaction']['user_id'])

    # Make inline keyboard from wallets by vertical list
    keyboard = []
    for wallet in wallets:
        keyboard.append([InlineKeyboardButton(f"{wallet.wallet_name}: {wallet.balance:,.0f} {currency}", callback_data=f"{wallet.wallet_id}|{wallet.wallet_name}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send request
    await update.message.reply_text("Chọn ví giao dịch:", reply_markup=reply_markup)
    return ASK_WALLET

async def ask_wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()
    wallet = query.data
    
    context.user_data['transaction']['wallet_id'] = query.data.split("|")[0]
    context.user_data['transaction']['wallet_name'] = query.data.split("|")[1]

    # Ask budget if spending
    if context.user_data['transaction']['type'] == models.EXPENSE:
        keyboard = []

        budgets = crud.get_budget_info(user_id=context.user_data['transaction']['user_id'])

        for budget in budgets:
            keyboard.append([InlineKeyboardButton(f"{budget.budget_name}: {budget.balance:,.0f} {currency}", callback_data=f"{budget.budget_id}|{budget.budget_name}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text("Chọn hũ chi tiêu:", reply_markup=reply_markup)
        return ASK_TRANSACTION_BUDGET
    else:
        await query.edit_message_text("Vui lòng nhập ghi chú:")
        return ASK_NOTE
    
async def ask_transaction_budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()

    context.user_data['transaction']['budget_id'] = query.data.split("|")[0]
    context.user_data['transaction']['budget_name'] = query.data.split("|")[1]

    await query.edit_message_text("Vui nhập ghi chú:")
    return ASK_NOTE

async def ask_note_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    
    context.user_data['transaction']['note'] = update.message.text

    coef = 1
    budget_name_msg = ""
    budget_balance_msg = ""
    if context.user_data['transaction']['type'] == models.EXPENSE:
        budget = crud.get_budget_info(user_id=context.user_data['transaction']['user_id'], budget_id=context.user_data['transaction']['budget_id'])
        budget_name_msg = f"\nHũ chi tiêu: {budget.budget_name}"
        budget_balance_msg = f"{budget.budget_name} : {(float(budget.balance) - context.user_data['transaction']['amount']):,.0f} {currency}"
        coef = -1

    wallet = crud.get_wallet_info(user_id=context.user_data['transaction']['user_id'], wallet_id=context.user_data['transaction']['wallet_id'])[0]

    # Confirm info
    confirm_text = f"""Xác nhận thông tin giao dịch:
Số tiền: {context.user_data['transaction']['amount']} 
Danh mục: {context.user_data['transaction']['category_name']} 
Ngày nhận: {context.user_data['transaction']['date']}
Ví giao dịch: {context.user_data['transaction']['wallet_name']} {budget_name_msg}
Ghi chú: {context.user_data['transaction']['note']}

Số dư sau giao dịch: 
{wallet.wallet_name}: {(float(wallet.balance) + coef * context.user_data['transaction']['amount']):,.0f} {currency}
{budget_balance_msg}
    """

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅", callback_data="confirm")],
        [InlineKeyboardButton("❌", callback_data="cancel")]
    ])
    await update.message.reply_text(confirm_text, reply_markup=reply_markup)
    return CONFIRM

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()
    if query.data == "cancel":
        await query.edit_message_text("❌ Đã hủy giao dịch.")
        print(Back.RED + "Đã hủy giao dịch." + Style.RESET_ALL)
        context.user_data.clear()
        return ConversationHandler.END
    
    
    # Add transaction to database
    transaction = crud.add_transaction(
        session=session,
        user_id=1,
        wallet_id=context.user_data['transaction']['wallet_id'],
        category_id=context.user_data['transaction']['category_id'],
        amount=context.user_data['transaction']['amount'],
        transaction_date=context.user_data['transaction']['date'],
        type=context.user_data['transaction']['type'],
        note=context.user_data['transaction']['note']
    )

    msg_budget_balance =""
    if (context.user_data['transaction']['type'] == models.EXPENSE):
        budget: models.Budget = crud.update_budget_balance(
            budget_id=context.user_data['transaction']['budget_id'], 
            amount=context.user_data['transaction']['amount'], 
            is_spending = True)
        msg_budget_balance = f"{budget.budget_name} : {budget.balance:,.0f} {currency}" 

    wallet = crud.get_wallet_info(user_id=context.user_data['transaction']['user_id'], wallet_id=context.user_data['transaction']['wallet_id'])[0]
    msg_wallet_balance = f"{wallet.wallet_name}: {wallet.balance:,.0f} {currency}"
    
    await query.message.reply_text(f"✅ Đã thêm giao dịch thành công")
    await query.message.reply_text(f"""Cập nhật số dư:
{msg_wallet_balance}
{msg_budget_balance}
    """)
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("CANCELED")
    context.user_data.clear()
    print("CANCELED")
    return ConversationHandler.END

add_transaction_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('add_transaction', ask_transaction_info)],
    states={
        ASK_TRANSACTION_TYPE: [CallbackQueryHandler(ask_transaction_type_handler)],
        ASK_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_amount_handler)],
        ASK_CATEGORY: [CallbackQueryHandler(ask_category_handler)],
        ASK_DATE: [CallbackQueryHandler(ask_date_handler)],
        ASK_DATE_OTHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date_other_handler)],
        ASK_WALLET: [CallbackQueryHandler(ask_wallet_handler)],
        ASK_TRANSACTION_BUDGET: [CallbackQueryHandler(ask_transaction_budget_handler)],
        ASK_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_note_handler)],
        CONFIRM: [CallbackQueryHandler(confirm_handler)]
        },
    fallbacks=[CommandHandler('cancel', cancel_handler)],
)

# =================== PIE CHART REPORT ===================
import altair as alt
PIE_CHART_SAVE_DIRECTORY = f"{CURRENT_DIRECTORY}/reports/pie_chart"

# Tạo thư mục nếu chưa có
os.makedirs(PIE_CHART_SAVE_DIRECTORY, exist_ok=True)

def make_pie_chart(df: pd.DataFrame, group_col: str, value_col: str, save_path: str, title: str):
    """
    Tạo biểu đồ tròn (pie chart) bằng Altair và lưu thành file PNG.
    
    Parameters:
        df (pd.DataFrame): Dữ liệu đầu vào
        group_col (str): Tên cột để nhóm dữ liệu (ví dụ: 'category' hoặc 'note')
        value_col (str): Tên cột chứa giá trị (ví dụ: 'amount')
        save_path (str): Đường dẫn file PNG để lưu
        title (str): Tiêu đề biểu đồ
    """
    if df.empty:
        return None

    # Đảm bảo cột giá trị là dạng float
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce').fillna(0.0)

    # Gộp và tính tổng
    grouped = df.groupby(group_col)[value_col].sum().reset_index()
    grouped = grouped.sort_values(by=value_col, ascending=False)

    if grouped.empty:
        return None

    # Thêm cột phần trăm (percentage)
    total = grouped[value_col].sum()
    grouped["percentage"] = (grouped[value_col] / total * 100).round(1)

    # Biểu đồ cơ bản
    chart = alt.Chart(grouped).mark_arc().encode(
        theta=alt.Theta(f"{value_col}", stack=True),
        color=alt.Color(f"{group_col}", legend=None)
    )

    # Vẽ phần miếng bánh
    pie = chart.mark_arc(radius=120, opacity=0.5, stroke='white', strokeWidth=2)

    # Hiển thị phần trăm
    percent = chart.mark_text(
        radius=70,
        size=24,
        font='Dongle',
        fontWeight='bold',
        color='black'
    ).encode(
        text=alt.Text("percentage:Q", format=".1f")
    )

    # Hiển thị nhãn
    label = chart.mark_text(
        radius=180,
        size=24,
        font='Dongle',
        fontWeight='bold',
        color='black'
    ).encode(
        text=alt.Text(f"{group_col}:N")
    )

    # Kết hợp và lưu
    final = (pie + percent + label)
    final.save(save_path, scale_factor=4)

    return save_path

def make_type_pie_chart(history: pd.DataFrame, type_name: str):
    pie_url = f"{PIE_CHART_SAVE_DIRECTORY}/pie_type_{get_this_month()}.png"
    expense = history[history["type"] == models.CategoryType(type_name)]

    print(expense)

    if expense.empty:
        return None

    return make_pie_chart(expense, "category", "amount", pie_url, f"Cơ cấu chi tiêu theo loại: {type_name}")


def make_category_pie_chart(history: pd.DataFrame, category_name: str):
    pie_url = f"{PIE_CHART_SAVE_DIRECTORY}/pie_category_{get_this_month()}.png"
    expense = history[history["category"] == category_name]
    
    if not expense:
        return None
    
    return make_pie_chart(expense, "note", "amount", pie_url, f"Cơ cấu chi tiêu trong hạng mục: {category_name}")

# =================== TABLE REPORT ===================
import imgkit
from html2image import Html2Image
from PIL import Image,ImageFont,ImageDraw,ImageChops

HISTORY_TABLE_DIRECTORY = f"{CURRENT_DIRECTORY}/reports/transaction_history_table"

# Tạo thư mục nếu chưa có
os.makedirs(HISTORY_TABLE_DIRECTORY, exist_ok=True)

def make_history_table(history: pd.DataFrame):
    
    df = history.drop(columns=["id"])
    df = df[["type","wallet", "date", "category", "amount", "wallet_balance", "note"]]
    df = df.rename(columns={
        "wallet": "Ví giao dịch",
        "date": "Ngày giao dịch",
        "category": "Danh mục",
        "amount": "Giá trị giao dịch",
        "wallet_balance": "Số dư tài khoản",
        "note": "Ghi chú"
    })

    # --------------------------
    # Highlight nếu Future Value > 300
    # --------------------------
    def highlight_rows(row):
        if row["type"] == models.CategoryType("Expense"):
            return ['background-color: #ffb6b6'] * len(row)
        return ['background-color: #a1ffb7'] * len(row)

    # --------------------------
    # Style bảng
    # --------------------------
    styled = (
        df.style
        .format({
            "Giá trị giao dịch": "{:,.0f}",
            "Số dư tài khoản": "{:,.0f}"
        })
        .apply(highlight_rows, axis=1)
        .set_table_styles([
            {'selector': 'table',
            'props': [
                ('border-collapse', 'collapse'),
                ('margin', 'auto'),
                ('font-family', '"Noto Color Emoji", Arial, sans-serif'),
                ('font-size', '16px'),
                ('color', '#333'),
                ('border', '2px solid #2f5597'),
                ('width', '100%'),
            ]},
            {'selector': 'th',
            'props': [
                ('background-color','#2f5597'),
                ('color', 'white'),
                ('padding', '8px'),
                ('text-align', 'center'),
                ('border', '1px solid #2f5597'),
                ('font-weight', 'bold'),
            ]},
            {'selector': 'td',
            'props': [
                ('padding', '8px'),
                ('text-align', 'center'),
                ('border', '1px solid #a6a6a6'),
            ]},
            {'selector': 'tr:nth-child(even)',
            'props': [('background-color', '#f9f9f9')]},
        ])
    )

    # 👉 Ẩn cột "type" (chỉ khi render)
    styled = styled.hide(axis="columns", subset=["type"])
    html_table = styled.to_html()

    # --------------------------
    # HTML — bảng căn giữa ngang, co giãn dọc
    # --------------------------
    html_full = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Báo cáo chi tiêu</title>
<style>
html, body {{
    margin: 0;
    padding: 0;
    background: #ffffff;
}}
body {{
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 40px 0;
}}
.wrapper {{
    display: inline-block;
    text-align: center;
}}
.container {{
    background: white;
    padding: 20px 40px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    border-radius: 12px;
    text-align: center;
    display: inline-block;
}}
h2 {{
    font-family: Arial, sans-serif;
    color: #2f5597;
    border-bottom: 2px solid #2f5597;
    display: inline-block;
    padding-bottom: 4px;
    margin-bottom: 10px;
}}
table {{
    margin: 0 auto;
}}
</style>
</head>
<body>
<div class="wrapper">
    <div class="container">
        {html_table}
    </div>
</div>
</body>
</html>
"""


    # --------------------------
    # Xuất ảnh (không đặt height)
    # --------------------------
    options = {
        'format': 'png',
        'encoding': "UTF-8",
        # 'width': 2000,   # chỉ cố định chiều ngang
        'quiet': ''
    }

    def trim_whitespace(im, bg_color=(255, 255, 255), tolerance=10):
        """Tự động cắt mép trắng (hoặc gần trắng)"""
        bg = Image.new(im.mode, im.size, bg_color)
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -tolerance)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)
        return im  # nếu không phát hiện được thì giữ nguyên

    def screenshot_auto(hti, html_str, save_path, width=800):
        temp_name = "_temp_preview.png"
        hti.screenshot(html_str=html_str, save_as=temp_name, size=(width, 1200))
        im = Image.open(f"{hti.output_path}/{temp_name}")
        cropped = trim_whitespace(im)
        cropped.save(save_path)
        im.close()

    # ---- Sử dụng ----
    hti = Html2Image(output_path=HISTORY_TABLE_DIRECTORY)
    save_path = f"{HISTORY_TABLE_DIRECTORY}/history_{get_this_month()}.png"
    screenshot_auto(hti, html_full, save_path, width=800)
    return save_path

# Conversation states
THIS_MONTH = "THIS_MONTH"
OTHER_MONTH = "OTHER_MONTH"

async def get_history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Tháng nay", callback_data="this")],
        [InlineKeyboardButton("Tháng khác", callback_data="other")]]
    )

    await update.message.reply_text("Hãy chọn:", reply_markup=reply_markup)
    return THIS_MONTH

async def get_history_this_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    if (update.callback_query.data == 'other'):
        await update.callback_query.edit_message_text("Hãy nhập tháng theo định dạng : \n<tháng>/<năm> hoặc <năm>-<tháng>")
        return OTHER_MONTH
    
    month = get_this_month()
    print(Fore.GREEN + f"month: {month}" + Style.RESET_ALL)
    
    transactions = crud.list_transactions(session,1,month)
    if (not transactions):
        await update.message.reply_text("Không có giao dịch trong thời gian truy vấn")
        return ConversationHandler.END
    dt = pd.DataFrame(transactions)
    table = make_history_table(dt)
    print("Table created at:", table)

    await update.callback_query.message.reply_photo(photo=open(table, "rb"))

    return ConversationHandler.END

async def get_history_other_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month = update.message.text
    if ('/' in month):
        month = month.split('/')
        month = f"{month[1]}-{month[0]}"
    elif ('-' not in month):
        await update.message.reply_text("Hãy nhập đúng định dạng : \n<tháng>/<năm> hoặc <năm>-<tháng>")
        return OTHER_MONTH
    
    print(Fore.GREEN + f"month: {month}" + Style.RESET_ALL)

    transactions = crud.list_transactions(session,1,month)
    if (not transactions):
        await update.message.reply_text("Không có giao dịch trong thời gian truy vấn")
        return ConversationHandler.END
    dt = pd.DataFrame(transactions)
    table = make_history_table(dt)
    # print("Table created at:", table)

    await update.message.reply_photo(photo=open(table, "rb"))

    return ConversationHandler.END

get_history_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('history', get_history_handler)],
    states={
        THIS_MONTH: [CallbackQueryHandler(get_history_this_month)],
        OTHER_MONTH: [MessageHandler(filters.TEXT & ~ filters.COMMAND, get_history_other_month)],
    },
    fallbacks=[CommandHandler('cancel', cancel_handler)],
)

# ============== Tạo report tháng ==============


REPORT_SAVE_DIRECTORY = f"{CURRENT_DIRECTORY}/reports/month_reports"
os.makedirs(REPORT_SAVE_DIRECTORY, exist_ok=True)

def make_monthly_report(month: str,user: str,):
    
    user_id = crud.get_user_info(session,user_name=user)[0].user_id
    if (not user_id):
        return "User not found"

    data = crud.list_transactions(session,user_id,month)
    if (not data):
        return "No transaction found"
    
    data.sort(key=lambda x: x['date'])
    for id in range(len(data)):
        data[id]["id"] = id
    df = pd.DataFrame(data)

    # print(df)

    # Tạo ảnh pie chart
    pie_chart = make_type_pie_chart(df, "Expense")

    # Tạo ảnh bảng lịch sử
    history_table = make_history_table(df)

    # Load created img (if no expense then no pie chart (piechart is 10x10px white blank img))
    if not pie_chart:
        pie_chart = Image.new("RGB", (10, 10), (255, 255, 255))
    else:
        pie_img = Image.open(pie_chart)
    history_img = Image.open(history_table)

    # Load imgs size
    pie_w,pie_h = pie_img.size
    history_w,history_h = history_img.size

    # Prepare for Tittle
    year,month = month.split("-")
    tittle = f"Báo cáo chi tiêu tháng {month} năm {year}"
    tittle_h = 200
    try:
        font = ImageFont.truetype("Dongle-Bold.ttf", 60)  # font của bạn
    except:
        font = ImageFont.load_default()

    # Resize pie img
    pie_w = int(pie_w * 0.4)
    pie_h = int(pie_h * 0.4)
    pie_img = pie_img.resize((pie_w,pie_h),Image.Resampling.LANCZOS)

    # Month report size
    report_w = max(pie_w,history_w)
    report_h = pie_h + history_h + tittle_h

    # New white blank img
    report_img = Image.new("RGB", (report_w, report_h), (255, 255, 255))

    # Draw tittle
    draw = ImageDraw.Draw(report_img)
    text_width = draw.textlength(tittle, font=font)
    x = (report_img.width - text_width) // 2
    y = (tittle_h - font.size) // 2
    draw.text((x, y), tittle, font=font, fill=(47, 85, 151))  # màu xanh đậm như bảng

    # Paste imgs
    report_img.paste(pie_img,((report_w - pie_w)//2,tittle_h))
    report_img.paste(history_img,((report_w - history_w)//2,pie_h + tittle_h))

    # Save report img
    save_path = f"{REPORT_SAVE_DIRECTORY}/report_{month}.png"
    report_img.save(save_path)
    return save_path

# ================== CONVERSATION: MONTHLY REPORT ==================

REPORT_THIS_MONTH = "REPORT_THIS_MONTH"
REPORT_OTHER_MONTH = "REPORT_OTHER_MONTH"

async def report_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bắt đầu quy trình yêu cầu báo cáo chi tiêu"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Tháng này", callback_data="this")],
        [InlineKeyboardButton("Tháng khác", callback_data="other")]
    ])
    await update.message.reply_text("🧾 Bạn muốn xem báo cáo chi tiêu tháng nào?", reply_markup=reply_markup)
    return REPORT_THIS_MONTH


async def report_this_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý khi chọn 'tháng này' hoặc chuyển sang nhập tháng khác"""
    await update.callback_query.answer()

    # Nếu chọn tháng khác → hỏi người dùng nhập tháng
    if update.callback_query.data == "other":
        await update.callback_query.edit_message_text(
            "📅 Hãy nhập tháng theo định dạng:\n`<tháng>/<năm>` hoặc `<năm>-<tháng>`"
        )
        return REPORT_OTHER_MONTH

    # Nếu chọn tháng này → tạo báo cáo trực tiếp
    month = get_this_month()
    user = update.callback_query.from_user.name
    report_path = make_monthly_report(month, user)

    if "User not found" in report_path:
        await update.callback_query.message.reply_text("⚠️ Không tìm thấy người dùng.")
        return ConversationHandler.END

    if "No transaction found" in report_path:
        await update.callback_query.message.reply_text("Không có giao dịch trong thời gian truy vấn")
        return ConversationHandler.END

    await update.callback_query.message.reply_photo(
        photo=open(report_path, "rb")
    )
    print(Fore.MAGENTA + f"REQUEST: Month report: {get_this_month()}" + Style.RESET_ALL)
    return ConversationHandler.END


async def report_other_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý khi người dùng nhập tháng tùy chọn"""
    month = update.message.text.strip()

    # Chuẩn hóa chuỗi tháng
    if '/' in month:
        try:
            m, y = month.split('/')
            month = f"{y}-{m.zfill(2)}"
        except ValueError:
            await update.message.reply_text("⚠️ Định dạng sai. Hãy nhập lại: `<tháng>/<năm>` hoặc `<năm>-<tháng>`")
            return REPORT_OTHER_MONTH
    elif '-' in month:
        parts = month.split('-')
        if len(parts) != 2:
            await update.message.reply_text("⚠️ Định dạng sai. Hãy nhập lại: `<tháng>/<năm>` hoặc `<năm>-<tháng>`")
            return REPORT_OTHER_MONTH
    else:
        await update.message.reply_text("⚠️ Định dạng sai. Hãy nhập lại: `<tháng>/<năm>` hoặc `<năm>-<tháng>`")
        return REPORT_OTHER_MONTH
    
    print(Fore.LIGHTCYAN_EX + f"month: {month}" + Style.RESET_ALL)

    # Tạo báo cáo
    user = update.callback_query.from_user.name
    report_path = make_monthly_report(month, user)

    if "User not found" in report_path:
        await update.message.reply_text("⚠️ Không tìm thấy người dùng.")
        return ConversationHandler.END

    if "No transaction found" in report_path:
        await update.message.reply_text("Không có giao dịch trong thời gian truy vấn")
        return ConversationHandler.END

    await update.message.reply_photo(
        photo=open(report_path, "rb")
    )
    return ConversationHandler.END


# ================== Conversation Handler ==================

report_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("report", report_entry)],
    states={
        REPORT_THIS_MONTH: [CallbackQueryHandler(report_this_month)],
        REPORT_OTHER_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_other_month)],
    },
    fallbacks=[CommandHandler("cancel", cancel_handler)],
)

# BUDGET
# region  
# ======================= ADD BUDGET ========================

ADD_BUDGET = "ADD_BUDGET"
ASK_BUDGET_AMOUNT = "ASK_BUDGET_AMOUNT"

budget_id = 0

async def add_budget_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.name
    print(Fore.LIGHTGREEN_EX + f"User: {user_name}" + Style.RESET_ALL)
    user_tele_id = update.message.from_user.id
    print(Fore.LIGHTRED_EX + f"User: {user_name}" + Style.RESET_ALL)

    if not is_user_valid(user_tele_id):
        print(Fore.LIGHTRED_EX + f"User: {user_name}| REJECTED: database unknown" + Style.RESET_ALL)
        await update.message.reply_text("⚠️ Người dùng không hợp lệ.")
        return ConversationHandler.END

    # Get user id
    user_id = crud.get_user_info(session, user_tele_id=user_tele_id)[0].user_id
    # user_id = 1 # For development

    # Get budget list
    budget_list = crud.get_budget_info(user_id)

    # Create keyboard
    keyboard = [[InlineKeyboardButton(text=f"{budget.budget_name}: {budget.balance:,.0f} {currency}", callback_data=budget.budget_id)] for budget in budget_list]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Hũ chi tiêu muốn bổ sung:", reply_markup=reply_markup)
    return ASK_BUDGET_AMOUNT


async def ask_budget_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global budget_id
    query = update.callback_query
    await query.answer()
    budget_id = int(query.data)
    print(Fore.LIGHTGREEN_EX + f"budget_id: {budget_id}" + Style.RESET_ALL)

    await query.message.reply_text("Bạn muốn bổ sung vào hũ bao nhiêu tiền ?")
    return ADD_BUDGET

async def add_budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global budget_id
    budget_amount = float(update.message.text)
    print(Fore.LIGHTGREEN_EX + f"budget_amount: {budget_amount}" + Style.RESET_ALL)

    print(Fore.MAGENTA + f"Add budget requested: budget_id: {budget_id}, budget_amount: {budget_amount}" + Style.RESET_ALL)
    # Add budget'
    if budget_id != 0:
        crud.update_budget_balance(budget_id=budget_id, session=session, amount=budget_amount, is_spending=False)

        # Report budget balance
        budget_info = crud.get_budget_info(session=session, budget_id=budget_id)
        await update.message.reply_text(f"{budget_info.budget_name}: {budget_info.balance:,.0f}")
        budget_id = 0
    else:
        await update.message.reply_text("Không tìm thấy hũ chi tiêu")

    return ConversationHandler.END


add_budget_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("add_budget", add_budget_entry)],
    states={
        ASK_BUDGET_AMOUNT: [CallbackQueryHandler(ask_budget_amount_handler)],
        ADD_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_budget_handler)],
    },
    fallbacks=[CommandHandler("cancel", cancel_handler)],
)

# ================== Budget balance request =====================
async def ask_budget_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_tele_id = update.message.from_user.id
    print(Fore.LIGHTRED_EX + f"User ID: {user_tele_id}" + Style.RESET_ALL)

    user = crud.get_user_info(session=session,user_tele_id=user_tele_id)[0]
    if not user:
        print(Fore.LIGHTRED_EX + f"User: {user_tele_id}| REJECTED: database unknown" + Style.RESET_ALL)
        await update.message.reply_text("⚠️ Người dùng không hợp lệ.")
        return ConversationHandler.END
    
    budgets = crud.get_budget_info(user_id = user.user_id)  
    msg= ""
    for budget in budgets:
        msg += f"{budget.budget_name}: {budget.balance:,.0f}\n"

    if not msg:
        msg = "Bạn không có hũ chi tiêu"
    await update.message.reply_text(msg)

# ===================== Create new budget =======================
ASK_NEW_BUDGET_NAME = "ASK_NEW_BUDGET_NAME"

async def create_budget_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Vui lòng nhập tên hũ chi tiêu")
    return ASK_NEW_BUDGET_NAME

async def create_new_budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    budget_name = update.message.text
    user_tele_id = update.message.from_user.id
    print(Fore.MAGENTA + f"User ID: {user_tele_id} try create new budget: {budget_name}" + Style.RESET_ALL)

    user = crud.get_user_info(session=session,user_tele_id=user_tele_id)[0]
    if not user:
        print(Fore.LIGHTRED_EX + f"User: {user_tele_id}| REJECTED: database unknown" + Style.RESET_ALL)
        await update.message.reply_text("⚠️ Người dùng không hợp lệ.")
        return ConversationHandler.END
    
    new_budget = crud.add_new_budget(budget_name=budget_name, user_id=user.user_id)
    if new_budget:
        await update.message.reply_text("Tạo hũ chi tiêu " + budget_name + " thành công")
        print(Fore.LIGHTGREEN_EX + f"User: {user_tele_id} create new budget: {budget_name} success" + Style.RESET_ALL)
    else:
        await update.message.reply_text("Tạo hũ chi tiêu không thành công")
        print(Fore.LIGHTRED_EX + f"User: {user_tele_id} create new budget: {budget_name} failed" + Style.RESET_ALL)
    return ConversationHandler.END


create_budget_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("create_budget", create_budget_start_handler)],
    states={
        ASK_NEW_BUDGET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_new_budget_handler)],
    },
    fallbacks=[CommandHandler("cancel", cancel_handler)],
)
#endregion

# WALLET
# region  
ASK_NEW_WALLET_NAME = "ASK_NEW_WALLET_NAME"

async def ask_wallet_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_tele_id = update.message.from_user.id
    print(Fore.LIGHTRED_EX + f"User ID: {user_tele_id}" + Style.RESET_ALL)

    user = crud.get_user_info(user_tele_id=user_tele_id)[0]
    if not user:
        print(Fore.LIGHTRED_EX + f"User: {user_tele_id}| REJECTED: database unknown" + Style.RESET_ALL)
        await update.message.reply_text("⚠️ Người dùng không hợp lệ.")
        return ConversationHandler.END

    wallets = crud.get_wallet_info(user_id=user.user_id)

    msg = ""
    for wallet in wallets:
        msg += f"{wallet.wallet_name}: {wallet.balance:,.0f}\n"

    if not msg:
        msg = "Bạn không có ví nào"

    await update.message.reply_text(msg)

async def create_wallet_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Vui lòng nhập tên ví mới")
    return ASK_NEW_WALLET_NAME

async def create_new_wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet_name = update.message.text
    user_tele_id = update.message.from_user.id
    print(Fore.MAGENTA + f"User ID: {user_tele_id} try create new wallet: {wallet_name}" + Style.RESET_ALL)

    user = crud.get_user_info(session=session,user_tele_id=user_tele_id)[0]
    if not user:
        print(Fore.LIGHTRED_EX + f"User: {user_tele_id}| REJECTED: database unknown" + Style.RESET_ALL)
        await update.message.reply_text("⚠️ Người dùng không hợp lệ.")
        return ConversationHandler.END
    
    new_wallet = crud.add_new_wallet(wallet_name=wallet_name, user_id=user.user_id)
    if new_wallet:
        await update.message.reply_text("Tạo ví " + wallet_name + " thành công")
        print(Fore.LIGHTGREEN_EX + f"User: {user_tele_id} create new wallet: {wallet_name} success" + Style.RESET_ALL)
    else:
        await update.message.reply_text("Tạo ví " + wallet_name + " không thành công")
        print(Fore.LIGHTRED_EX + f"User: {user_tele_id} create new wallet: {wallet_name} failed" + Style.RESET_ALL)
    return ConversationHandler.END


create_wallet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("create_wallet", create_wallet_start_handler)],
    states={
        ASK_NEW_WALLET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_new_wallet_handler)],
    },
    fallbacks=[CommandHandler("cancel", cancel_handler)],
)
# endregion


# region CATEGORY MANAGEMENT
ASK_NEW_CATEGORY_NAME = "ASK_NEW_CATEGORY_NAME"
ASK_NEW_CATEGOR_TYPE = "ASK_NEW_CATEGOR_TYPE"

async def create_category_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Vui lòng nhập tên danh mục")
    user_tele_id = update.message.from_user.id

    user = crud.get_user_info(session=session,user_tele_id=user_tele_id)[0]
    if not user:
        print(Fore.LIGHTRED_EX + f"User: {user_tele_id}| REJECTED: database unknown" + Style.RESET_ALL)
        await update.message.reply_text("⚠️ Người dùng không hợp lệ.")
        return ConversationHandler.END

    context.user_data['category'] = {
        'type': models.CategoryType.expense,
        'name': None,
        'user_id': user.user_id,
        'user_tele_id': user_tele_id
    }
    return ASK_NEW_CATEGORY_NAME

async def ask_new_category_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category_name = update.message.text
    
    context.user_data['category']['name'] = category_name

    keyboard = [
        [
            InlineKeyboardButton("Chi tiêu", callback_data=models.EXPENSE),
            InlineKeyboardButton("Thu nhập", callback_data=models.INCOME),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Vui lòng chọn loại danh mục", reply_markup=reply_markup)
    
    return ASK_NEW_CATEGOR_TYPE

async def create_new_category_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.callback_query.answer()

    category_type = models.CategoryType(update.callback_query.data)
    user_id = context.user_data['category']['user_id']
    category_name = context.user_data['category']['name']
    user_tele_id = context.user_data['category']['user_tele_id']
    print(Fore.MAGENTA + f"User ID: {user_tele_id} try create new category: {category_name} type: {category_type}" + Style.RESET_ALL)

    new_category = crud.add_new_category(category_name=category_name, user_id=user_id, type=category_type)
    if new_category:
        await update.callback_query.message.reply_text("Tạo danh mục " + category_name + " thành công")
        print(Fore.LIGHTGREEN_EX + f"User: {user_tele_id} create new category: {category_name} success" + Style.RESET_ALL)
    else:
        await update.callback_query.message.reply_text("Tạo danh mục " + category_name + " không thành công")
        print(Fore.LIGHTRED_EX + f"User: {user_tele_id} create new category: {category_name} failed" + Style.RESET_ALL)
    

create_category_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("create_category", create_category_start_handler)],
    states={
        ASK_NEW_CATEGORY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_new_category_name_handler)],
        ASK_NEW_CATEGOR_TYPE: [CallbackQueryHandler(create_new_category_type_handler)],
    },
    fallbacks=[CommandHandler("cancel", cancel_handler)],
)

#endregion

# WISHLIST
# region
# ================== ADD WISHLIST CONVERSATION ===================
ASK_NEW_WISHLIST_NAME = "ASK_NEW_WISHLIST_NAME"
ASK_NEW_WISHLIST_COST = "ASK_NEW_WISHLIST_COST"
ASK_NEW_WISHLIST_CONFIRM = "ASK_NEW_WISHLIST_CONFIRM"

async def ask_add_wishlist_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Vui lòng nhập tên cho kế hoạch chi tiêu")

    context.user_data['wishlist'] = {
        'name': None,
        'cost': None,
        'user_id' : crud.get_user_info(session=session,user_tele_id=update.message.from_user.id)[0].user_id 
    }

    return ASK_NEW_WISHLIST_NAME

async def ask_new_wishlist_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wishlist_name = update.message.text
    context.user_data['wishlist']['name'] = wishlist_name
    await update.message.reply_text("Chi phí chi tiêu:")
    return ASK_NEW_WISHLIST_COST

async def ask_new_wishlist_cost_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wishlist_cost = float(update.message.text)
    context.user_data['wishlist']['cost'] = wishlist_cost

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅", callback_data="confirm")],
        [InlineKeyboardButton("❌", callback_data="cancel")]
    ])

    await update.message.reply_text("Xác nhận kế hoạch chi tiêu:\n"
        + "Tên: " + context.user_data['wishlist']['name'] + "\n"
        + "Chi phí: " + str(context.user_data['wishlist']['cost']) + str(currency),
        reply_markup=reply_markup
    )

    return ASK_NEW_WISHLIST_CONFIRM

async def ask_new_wishlist_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    wishlist_name = context.user_data['wishlist']['name']
    wishlist_cost = context.user_data['wishlist']['cost']
    user_id = context.user_data['wishlist']['user_id']

    new_wishlist = crud.add_wishlist(wishlist_name=wishlist_name, user_id=user_id, cost=wishlist_cost)
    if not new_wishlist:
        await update.callback_query.message.reply_text("❌ Tạo chi tiêu không thành công")
        return ConversationHandler.END
    else:
        await update.callback_query.message.reply_text("✅ Tạo chi tiêu thành công")
        return ConversationHandler.END
    

add_wishlist_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("create_wishlist", ask_add_wishlist_start_handler)],
    states={
        ASK_NEW_WISHLIST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_new_wishlist_name_handler)],
        ASK_NEW_WISHLIST_COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_new_wishlist_cost_handler)],
        ASK_NEW_WISHLIST_CONFIRM: [CallbackQueryHandler(ask_new_wishlist_confirm_handler)],
    },
    fallbacks=[CommandHandler("cancel", cancel_handler)],
)

# ====================== WISHLIST INFO REQUEST ======================

import pandas as pd

def format_wishlist_table(wishlists, currency="₫"):
    # Tạo DataFrame từ danh sách ORM object
    df = pd.DataFrame([{
        "Kế hoạch": w.wish_name,
        "Chi phí": f"{w.cost:,.0f} {currency}"
    } for w in wishlists])

    # Xuất ra dạng bảng văn bản đẹp
    return df


async def ask_wishlist_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = crud.get_user_info(session=session, user_tele_id=update.message.from_user.id)[0]
    wishlists = crud.get_wishlist(user_id=user.user_id)

    keyboard = []
    for wishlist in wishlists:
        keyboard.append([
            InlineKeyboardButton(text=f"{wishlist.wish_name}", callback_data=f"wish_{wishlist.wish_id}"),
            InlineKeyboardButton(text=f"{wishlist.cost:,.0f} {currency}", callback_data=f"cost_{wishlist.wish_id}")
        ])

    total_cost = sum([wishlist.cost for wishlist in wishlists])
    keyboard.append([
        InlineKeyboardButton(text=f"💰 Tổng: {total_cost:,.0f} {currency}", callback_data="total")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Gửi dưới dạng code block để hiển thị đẹp
    await update.message.reply_text(f"📋 Danh sách dự chi:",reply_markup=reply_markup)
    return ConversationHandler.END

# ====================== WISHLIST EXECUTE CONVERSATION ======================
ASK_EXECUTE_WISHLIST_ID = "ASK_EXECUTE_WISHLIST"
ASK_EXECUTE_WISHLIST_CONFIRMATION = "ASK_EXECUTE_WISHLIST_CONFIRMATION"

async def ask_execute_wishlist_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id=crud.get_user_info(session=session,user_tele_id=update.message.from_user.id)[0].user_id
    wishlists = crud.get_wishlist(user_id=user_id)

    keyboard = [[InlineKeyboardButton(text = f"{wishlist.wish_name}: {wishlist.cost:,.0f} {currency}", callback_data=str(wishlist.wish_id))] for wishlist in wishlists]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Hãy chọn chi tiêu muốn giải ngân:\n", reply_markup=reply_markup)

    context.user_data['user_id'] = user_id 
    context.user_data['conversation_context'] = "execute_wishlist"

    return ASK_EXECUTE_WISHLIST_ID

async def ask_execute_wishlist_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    context.user_data['wishlist_id'] = update.callback_query.data

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅", callback_data="confirm")],
        [InlineKeyboardButton("❌", callback_data="cancel")]
    ])
    await update.callback_query.message.reply_text("Xác nhận giải ngân", reply_markup=reply_markup)

    return ASK_EXECUTE_WISHLIST_CONFIRMATION

async def ask_execute_wishlist_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    if (update.callback_query.data == "cancel"):
        await update.callback_query.message.reply_text("Đã hủy giải ngân")
        context.user_data.clear()
        return ConversationHandler.END

    crud.execute_wishlist(
        wishlist_id=context.user_data['wishlist_id']
    )

    await update.callback_query.message.reply_text("Giải ngân thành công")
    context.user_data.clear()
    return ConversationHandler.END

execute_wishlist_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("execute_wishlist", ask_execute_wishlist_start_handler)],
    states={
        ASK_EXECUTE_WISHLIST_ID: [CallbackQueryHandler(ask_execute_wishlist_id_handler)],
        ASK_EXECUTE_WISHLIST_CONFIRMATION: [CallbackQueryHandler(ask_execute_wishlist_confirmation_handler)],
    },
    fallbacks=[CommandHandler("cancel", cancel_handler)],
)

# endregion