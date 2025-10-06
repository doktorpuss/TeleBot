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

    await query.edit_message_text(f"Đã chọn danh mục: {category}\nNgày giao dịch:",reply_markup=reply_markup)
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
        keyboard.append([InlineKeyboardButton(wallet.wallet_name, callback_data=wallet.wallet_name)])
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

# =================== GENERATE REPORT ===================

import plotly.graph_objects as go
import plotly.io as pio

# # Bỏ sandbox để tránh lỗi "browser closed immediately"
# pio.defaults.chromium_args = ["--no-sandbox"]

# # Nếu cần chỉ định trình duyệt cụ thể (tùy hệ thống)
# pio.defaults.chromium_executable = "/snap/bin/chromium"  # hoặc "/usr/bin/google-chrome"


REPORT_SAVE_DIRECTORY = "reports"
PIE_CHART_SAVE_DIRECTORY = "pie_chart"
CREATED_DATE =  datetime.datetime.now().__str__().split()[0]

def make_report_img(history: pd.DataFrame, month: str):
    report_url = f"{CURRENT_DIRECTORY}/{REPORT_SAVE_DIRECTORY}/report_expense_pie_{month}.png"

    fig, ax = plt.subplots(figsize=(10, len(history) * 0.4 + 1))
    ax.axis("off")
    table = ax.table(
        cellText=history.values,
        colLabels=history.columns,
        loc="center",
        cellLoc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.3)

    plt.title(f"Lịch sử giao dịch {month}", pad=20)
    plt.savefig(report_url)
    plt.close()

    return report_url

    # print(f"✅ Báo cáo đã tạo xong cho {month}:\n - report_expense_pie_{month}.png\n - report_transactions_{month}.png")

def make_type_pie_chart(history: pd.DataFrame, type: str):
    pie_url = f"{CURRENT_DIRECTORY}/{PIE_CHART_SAVE_DIRECTORY}/pie_type_{CREATED_DATE}.png"

    expense = history[history["type"] == type]
    expense = expense.groupby(["category"])["amount"].sum().reset_index()
    expense = expense.sort_values(by="amount", ascending=False)

    if expense.empty:
        return None

    fig = go.Figure(data=[
        go.Pie(
            labels=expense["category"],
            values=expense["amount"],
            textinfo="label+percent",
            # insidetextorientation="radial",
            hoverinfo="label+value+percent",
            textposition="outside"
        )
    ])

    fig.update_layout(
        # title=f"Cơ cấu chi tiêu theo loại: {type}",
        font=dict(family="Dongle", size=40, color="black"),
        showlegend=False,
        margin=dict(t=80, b=20, l=20, r=20),
        width=700,
        height=700
    )

    fig.update_traces(
    textfont=dict(family="Dongle, sans-serif", size=40),
    texttemplate="<b>%{label}</b><br>%{percent}"
    )

    os.makedirs(f"{CURRENT_DIRECTORY}/{PIE_CHART_SAVE_DIRECTORY}", exist_ok=True)
    fig.write_image(pie_url)  # cần cài kaleido
    return pie_url


def make_category_pie_chart(history: pd.DataFrame, category: str):
    pie_url = f"{CURRENT_DIRECTORY}/{PIE_CHART_SAVE_DIRECTORY}/pie_category_{CREATED_DATE}.png"

    expense = history[history["category"] == category]
    expense = expense.groupby(["note"])["amount"].sum().reset_index()
    expense = expense.sort_values(by="amount", ascending=False)

    if expense.empty:
        return None

    fig = go.Figure(data=[
        go.Pie(
            labels=expense["note"],
            values=expense["amount"],
            textinfo="label+percent",
            insidetextorientation="radial",
            hoverinfo="label+value+percent",
        )
    ])

    fig.update_layout(
        # title=f"Cơ cấu chi tiêu trong hạng mục: {category}",
        font=dict(size=30),
        showlegend=False,
        margin=dict(t=80, b=20, l=20, r=20),
        width=700,
        height=700
    )

    os.makedirs(f"{CURRENT_DIRECTORY}/{PIE_CHART_SAVE_DIRECTORY}", exist_ok=True)
    fig.write_image(pie_url)
    return pie_url
