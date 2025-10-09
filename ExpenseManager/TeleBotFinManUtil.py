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

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

session = db.get_session()

class TransactionInfo:
    date = ""
    note = ""
    amount : float = 0.0
    category_id : int = 1
    category_name : str = ""
    wallet_id : int = 1
    wallet_name: str = ""
    type : models.CategoryType = models.CategoryType.expense


transaction_info = TransactionInfo()

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

# =================== ADD INCOME/EXPENSE CONVERSATION ===================
ASK_AMOUNT = "ASK_AMOUNT"
ASK_CATEGORY = "ASK_CATEGORY"
ASK_DATE = "ASK_DATE"
ASK_DATE_OTHER = "ASK_DATE_OTHER"
ASK_WALLET = "ASK_WALLET"
ASK_NOTE = "ASK_NOTE"
ADD_INCOME = "ADD_INCOME"
CONFIRM = "CONFIRM"


reply_markup = None

async def ask_income_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    global transaction_info
    print(Back.MAGENTA + "Bắt đầu thêm thu nhập" + Style.RESET_ALL)
    await update.message.reply_text("Nhập số tiền thu nhập:")
    transaction_info.type = models.CategoryType.income
    return ASK_AMOUNT

async def ask_expense_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    global transaction_info
    print(Back.MAGENTA + "Bắt đầu thêm chi tiêu" + Style.RESET_ALL)
    await update.message.reply_text("Nhập số tiền chi tiêu:")
    transaction_info.type = models.CategoryType.expense
    return ASK_AMOUNT

async def ask_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    global transaction_info, reply_markup
    try:
        transaction_info.amount = float(update.message.text)

        # Get category list depend on type
        if transaction_info.type == models.CategoryType.expense:
            categories = crud.get_categories_list(session=session, user_id=1, type=models.CategoryType.expense)
        else:
            categories = crud.get_categories_list(session=session, user_id=1, type=models.CategoryType.income)

        #make inline keyboard from categories by vertical list
        keyboard = []
        for category in categories:
            keyboard.append([InlineKeyboardButton(category, callback_data=category)])
        reply_markup = InlineKeyboardMarkup(keyboard)

        #Send request
        await update.message.reply_text("Nhập danh mục thu nhập:", reply_markup=reply_markup)
        return ASK_CATEGORY
    
    except ValueError:
        await update.message.reply_text("Số tiền không hợp lệ. Vui lòng nhập lại số tiền thu nhập:")
        return ASK_AMOUNT

async def ask_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()
    category = query.data

    category_id = crud.get_category_id(session=session, user_name="Quang", category_name=category)
    if not category_id:
        await query.edit_message_text("Danh mục không hợp lệ. Vui lòng chọn lại:", reply_markup=reply_markup)
        return ASK_CATEGORY
    
    transaction_info.category_id = category_id
    transaction_info.category_name = category

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hôm nay", callback_data="today")],
                    [InlineKeyboardButton("Hôm qua", callback_data="day_before")],
                    [InlineKeyboardButton("Ngày khác", callback_data="other")]])
    
    if transaction_info.type == models.CategoryType.expense:
        budget_id = crud.get_category_info(session=session, category_id=category_id).budget_id
        budget_info = crud.get_budget_info(session=session, budget_id=budget_id)
        await query.message.reply_text(f"danh mục [{category}] \n{budget_info.budget_name}: {budget_info.balance:,.0f}\nNgày giao dịch:",reply_markup=reply_markup)
    else:
        await query.edit_message_text(f"danh mục [{category}] \nNgày giao dịch:",reply_markup=reply_markup)
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
    
    transaction_info.date = date_str

    # Get wallet list
    wallets = crud.list_wallets(session=session, user_id=1)

    # Make inline keyboard from wallets by vertical list
    keyboard = []
    for wallet in wallets:
        keyboard.append([InlineKeyboardButton(f"{wallet.wallet_name}: {wallet.balance:,.0f} VND", callback_data=wallet.wallet_name)])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send request
    await query.edit_message_text("Chọn ví giao dịch:", reply_markup=reply_markup)
    return ASK_WALLET

async def ask_date_other_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    date_str = normalize_date_string(update.message.text)

    if date_str == "Date unrecognized":
        await update.message.reply_text("Ngày không hợp lệ. Vui lòng nhập lại ngày giao dịch (YYYY-MM-DD hoặc DD/MM/YYYY):")
        return ASK_DATE
    
    transaction_info.date = date_str

    # Get wallet list
    wallets = crud.list_wallets(session=session, user_id=1)

    # Make inline keyboard from wallets by vertical list
    keyboard = []
    for wallet in wallets:
        keyboard.append([InlineKeyboardButton(wallet.wallet_name, callback_data=wallet.wallet_name)])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send request
    await update.message.reply_text("Chọn ví giao dịch:", reply_markup=reply_markup)
    return ASK_WALLET

async def ask_wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()
    wallet = query.data

    wallet_id = crud.get_wallet_id(session=session, user_id=1, wallet_name=wallet)
    if not wallet_id:
        await query.edit_message_text("Ví không hợp lệ. Vui lòng chọn lại:", reply_markup=reply_markup)
        return ASK_WALLET
    
    transaction_info.wallet_name = wallet
    transaction_info.wallet_id = wallet_id

    await query.edit_message_text(f"Đã chọn ví: {wallet}\nNhập ghi chú:")
    return ASK_NOTE

async def ask_note_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    
    transaction_info.note = update.message.text

    coef = 1 if transaction_info.type == models.CategoryType.income else -1

    # Confirm info
    confirm_text = f"""Xác nhận thông tin giao dịch:
Số tiền: {transaction_info.amount}
Danh mục: {transaction_info.category_name}
Ngày nhận: {transaction_info.date}
Ví giao dịch: {transaction_info.wallet_name}
Ghi chú: {transaction_info.note}

Số dư ví sau giao dịch: {crud.get_wallet_balance(session=session, wallet_id=transaction_info.wallet_id) + transaction_info.amount * coef}
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
        return ConversationHandler.END
    
    if (transaction_info.type == models.CategoryType.expense):
        # Add expense to database
        expense = crud.add_expense(
            session=session,
            user_id=1,
            wallet_id=transaction_info.wallet_id,
            category_id=transaction_info.category_id,
            amount=transaction_info.amount,
            expense_date=transaction_info.date,
            note=transaction_info.note
        )
        await query.edit_message_text(f"✅ Đã thêm chi tiêu thành công")

        # Report budget balance
        budget_id = crud.get_category_info(session, transaction_info.category_id).budget_id # get budget id from category
        budget_info = crud.get_budget_info(session=session, budget_id=budget_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{budget_info.budget_name}: {budget_info.balance:,.0f}")

        print(Back.GREEN + f"Đã thêm chi tiêu với ID: {expense.expense_id}" + Style.RESET_ALL)
    else:
        # Add income to database
        income = crud.add_income(
            session=session,
            user_id=1,
            wallet_id=transaction_info.wallet_id,
            category_id=transaction_info.category_id,
            amount=transaction_info.amount,
            income_date=transaction_info.date,
            note=transaction_info.note
        )
        await query.edit_message_text(f"✅ Đã thêm thu nhập thành công")
        print(Back.GREEN + f"Đã thêm thu nhập với ID: {income.income_id}" + Style.RESET_ALL)

    return ConversationHandler.END

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("CANCELED")
    return ConversationHandler.END

add_income_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('add_income', ask_income_info)],
    states={
        
        ASK_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_amount_handler)],
        ASK_CATEGORY: [CallbackQueryHandler(ask_category_handler)],
        ASK_DATE: [CallbackQueryHandler(ask_date_handler)],
        ASK_DATE_OTHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date_other_handler)],
        ASK_WALLET: [CallbackQueryHandler(ask_wallet_handler)],
        ASK_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_note_handler)],
        CONFIRM: [CallbackQueryHandler(confirm_handler)]
        },
    fallbacks=[CommandHandler('cancel', cancel_handler)],
)

add_expense_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('add_expense', ask_expense_info)],
    states={
        
        ASK_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_amount_handler)],
        ASK_CATEGORY: [CallbackQueryHandler(ask_category_handler)],
        ASK_DATE: [CallbackQueryHandler(ask_date_handler)],
        ASK_DATE_OTHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date_other_handler)],
        ASK_WALLET: [CallbackQueryHandler(ask_wallet_handler)],
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
    expense = history[history["type"] == type_name]

    if not expense:
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
        if row["type"] == "expense" :
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
    <title>Sample Dataset</title>
    <style>
    body {{
        background: #ffffff;
        margin: 0;
        display: flex;
        justify-content: center;
        padding: 40px 0;
    }}
    .container {{
        background: white;
        padding: 20px 40px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        border-radius: 12px;
        text-align: center;
    }}
    h2 {{
        font-family: Arial, sans-serif;
        color: #2f5597;
        border-bottom: 2px solid #2f5597;
        display: inline-block;
        padding-bottom: 4px;
        margin-bottom: 10px;
    }}
    </style>
    </head>
    <body>
    <div class="container">
        {html_table}
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

    save_path = f"{HISTORY_TABLE_DIRECTORY}/history_{get_this_month()}.png"
    imgkit.from_string(html_full, save_path, options=options)
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
from PIL import Image,ImageFont,ImageDraw

REPORT_SAVE_DIRECTORY = f"{CURRENT_DIRECTORY}/reports/month_reports"
os.makedirs(REPORT_SAVE_DIRECTORY, exist_ok=True)

def make_monthly_report(month: str,user: str,):
    
    user_id = crud.get_user_id(session,user)
    if (not user_id):
        return "User not found"

    data = crud.list_transactions(session,user_id,month)
    if (not data):
        return "No transaction found"
    
    df = pd.DataFrame(data)

    # Tạo ảnh pie chart
    pie_chart = make_type_pie_chart(df, "expense")

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
    user = "Quang"  # hoặc "Quang" nếu bạn test cố định
    report_path = make_monthly_report(month, user)

    if "User not found" in report_path:
        await update.message.reply_text("⚠️ Không tìm thấy người dùng.")
        return ConversationHandler.END

    if "No transaction found" in report_path:
        await update.message.reply_text("Không có giao dịch trong thời gian truy vấn")
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
    # user = update.effective_user.first_name
    user = "Quang"
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

# ======================= ADD BUDGET ========================

ADD_BUDGET = "ADD_BUDGET"
ASK_BUDGET_AMOUNT = "ASK_BUDGET_AMOUNT"

budget_id = 0

async def add_budget_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.name
    print(Fore.LIGHTGREEN_EX + f"User: {user_name}" + Style.RESET_ALL)

    # Get user id
    user_id = crud.get_user_id(session, user_name)
    user_id = 1 # For development

    # Get budget list
    budget_list = crud.get_budget_list(session,user_id)

    # Create keyboard
    keyboard = [[InlineKeyboardButton(text=f"{budget['name']}: {budget['balance']} VND", callback_data=budget['id'])] for budget in budget_list]

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