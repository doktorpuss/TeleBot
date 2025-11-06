from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler,
    CallbackQueryHandler
)

# Define states
MAIN_MENU = 0
FINMAN_SERVICE = 1
SCHEDULER_SERVICE = 2

# ==================== MAIN MENU ====================
async def start_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point - Shows main menu"""
    keyboard = [
        [InlineKeyboardButton("💰 Financial Manager", callback_data="finman_service")],
        [InlineKeyboardButton("📅 Scheduler Service", callback_data="scheduler_service")],
        [InlineKeyboardButton("❌ Exit", callback_data="exit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "🤖 *Welcome to IRI Bot*\n\nPlease select a service:"
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.message.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    return MAIN_MENU


# ==================== FINMAN SERVICE MENU ====================
async def finman_service_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows Financial Manager submenu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📊 Report", callback_data="report_request")],
        [InlineKeyboardButton("➕ Add Transaction", callback_data="add_transaction")],
        [InlineKeyboardButton("👛 Wallet Management", callback_data="wallet_management")],
        [InlineKeyboardButton("💳 Budget Management", callback_data="budget_management")],
        [InlineKeyboardButton("🏷️ Add Category", callback_data="category_add")],
        [InlineKeyboardButton("🎯 Wishlist Management", callback_data="wishlist_management")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "💰 *Financial Manager*\n\nSelect an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return FINMAN_SERVICE


# ==================== WALLET MANAGEMENT ====================
async def wallet_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows Wallet Management submenu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("ℹ️ Wallet Info", callback_data="wallet_info")],
        [InlineKeyboardButton("➕ Add Wallet", callback_data="wallet_add")],
        [InlineKeyboardButton("🔙 Back", callback_data="finman_service")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "👛 *Wallet Management*\n\nSelect an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return FINMAN_SERVICE


# ==================== BUDGET MANAGEMENT ====================
async def budget_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows Budget Management submenu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("ℹ️ Budget Info", callback_data="budget_info")],
        [InlineKeyboardButton("➕ Add Budget", callback_data="budget_add")],
        [InlineKeyboardButton("🔙 Back", callback_data="finman_service")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "💳 *Budget Management*\n\nSelect an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return FINMAN_SERVICE


# ==================== WISHLIST MANAGEMENT ====================
async def wishlist_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows Wishlist Management submenu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("ℹ️ Wishlist Info", callback_data="wishlist_info")],
        [InlineKeyboardButton("➕ Add Wishlist", callback_data="wishlist_add")],
        [InlineKeyboardButton("✅ Execute Wishlist", callback_data="wishlist_execute")],
        [InlineKeyboardButton("🔙 Back", callback_data="finman_service")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "🎯 *Wishlist Management*\n\nSelect an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return FINMAN_SERVICE


# ==================== SCHEDULER SERVICE MENU ====================
async def scheduler_service_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows Scheduler Service submenu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("➕ Create Event", callback_data="create_event")],
        [InlineKeyboardButton("📋 List Events", callback_data="list_events")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "📅 *Scheduler Service*\n\nSelect an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return SCHEDULER_SERVICE


# ==================== LIST EVENTS MENU ====================
async def list_events_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows List Events submenu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📅 Today", callback_data="list_event_today")],
        [InlineKeyboardButton("📆 This Week", callback_data="list_event_week")],
        [InlineKeyboardButton("🗓️ This Month", callback_data="list_event_month")],
        [InlineKeyboardButton("🔍 Custom", callback_data="list_event_custom")],
        [InlineKeyboardButton("🔙 Back", callback_data="scheduler_service")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "📋 *List Events*\n\nSelect time range:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return SCHEDULER_SERVICE


# ==================== CALLBACK ROUTER ====================
async def button_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routes callback queries to appropriate handlers or conversation handlers"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Main menu navigation
    if callback_data == "main_menu":
        return await start_main_menu(update, context)
    
    # Service menus
    elif callback_data == "finman_service":
        return await finman_service_menu(update, context)
    
    elif callback_data == "scheduler_service":
        return await scheduler_service_menu(update, context)
    
    # Wallet Management
    elif callback_data == "wallet_management":
        return await wallet_management_menu(update, context)
    
    # Budget Management
    elif callback_data == "budget_management":
        return await budget_management_menu(update, context)
    
    # Wishlist Management
    elif callback_data == "wishlist_management":
        return await wishlist_management_menu(update, context)
    
    # List Events
    elif callback_data == "list_events":
        return await list_events_menu(update, context)
    
    # Exit
    elif callback_data == "exit":
        await query.message.edit_text("👋 Goodbye! Use /start to return to menu.")
        return ConversationHandler.END
    
    # If callback is for triggering existing conversation handlers
    # These will end this conversation and trigger the respective conversation handler
    elif callback_data in ["report_request", "add_transaction", "wallet_info", "wallet_add", 
                           "budget_info", "budget_add", "category_add", "wishlist_info", 
                           "wishlist_add", "wishlist_execute", "create_event", 
                           "list_event_today", "list_event_week", "list_event_month", "list_event_custom"]:
        
        # Store the selected action in context
        context.user_data['pending_action'] = callback_data
        
        # Inform user to use the specific command
        command_map = {
            "report_request": "/report",
            "add_transaction": "/add_transaction",
            "wallet_info": "/wallet_info",
            "wallet_add": "/create_wallet",
            "budget_info": "/budget_info",
            "budget_add": "/add_budget",
            "category_add": "/create_category",
            "wishlist_info": "/wishlist_info",
            "wishlist_add": "/create_wishlist",
            "wishlist_execute": "/execute_wishlist",
            "create_event": "/create_event",
            "list_event_today": "/today",
            "list_event_week": "/week",
            "list_event_month": "/month",
            "list_event_custom": "/event"
        }
        
        command = command_map.get(callback_data, "")
        await query.message.edit_text(
            f"🔄 Please use the command: {command}\n\n"
            f"Or use /start to return to menu."
        )
        return ConversationHandler.END


# ==================== CANCEL HANDLER ====================
async def cancel_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    await update.message.reply_text("👋 Operation cancelled. Use /start to return to menu.")
    return ConversationHandler.END


# ==================== CONVERSATION HANDLER ====================
main_menu_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start_main_menu)],
    states={
        MAIN_MENU: [
            CallbackQueryHandler(button_callback_router)
        ],
        FINMAN_SERVICE: [
            CallbackQueryHandler(button_callback_router)
        ],
        SCHEDULER_SERVICE: [
            CallbackQueryHandler(button_callback_router)
        ],
    },
    fallbacks=[
        CommandHandler('cancel', cancel_main_menu),
        CommandHandler('start', start_main_menu)
    ],
    allow_reentry=True
)