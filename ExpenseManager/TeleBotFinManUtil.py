from ExpenseManager import crud,db,models
import datetime
from colorama import Fore,Back,Style
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler,CommandHandler,MessageHandler,filters,ContextTypes,ConversationHandler


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

# income = crud.add_income(
#     session,
#     user_id=1,
#     wallet_id=1,
#     category_id=1,
#     amount=70000,
#     income_date="2025-10-1",
#     note="Test"
# )
# print("Đã thêm:", income.income_id)