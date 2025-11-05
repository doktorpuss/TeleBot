import secrete
from Scheduler import TeleBotScheduleUtil as scheduler
from ExpenseManager import TeleBotFinManUtil as finman
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes,ConversationHandler


if __name__ == '__main__':
    print("Starting IRI")
    app = Application.builder().token(secrete.TOKEN).build()

    #COMMAND
    # app.add_handler(CommandHandler('start',scheduler.start_handler))
    # app.add_handler(CommandHandler('end',scheduler.end_handler))
    app.add_handler(CommandHandler('today',scheduler.CMD_today_handler))
    app.add_handler(CommandHandler('week',scheduler.CMD_week_handler))
    app.add_handler(CommandHandler('month',scheduler.CMD_month_handler))
    app.add_handler(CommandHandler('register',finman.registration)) # command : /register
    app.add_handler(CommandHandler('update_registration_mode',finman.registration_allow_update)) # command : /update_registration_mode
    app.add_handler(CommandHandler('budget_info',finman.ask_budget_balance_handler)) # command : /budget_info
    app.add_handler(CommandHandler('wallet_info',finman.ask_wallet_balance_handler)) # command : /wallet_info
    app.add_handler(CommandHandler('wishlist_info',finman.ask_wishlist_handler)) # command : /wishlist_info
    
    # #CONVERSATION
    app.add_handler(scheduler.create_event_conv_handler) # command : /create_event
    app.add_handler(scheduler.get_event_conv_handler) # command : /event
    app.add_handler(finman.add_transaction_conv_handler) # command : /add_transaction
    app.add_handler(finman.report_conv_handler) #command : /report
    app.add_handler(finman.add_budget_conv_handler) # command : /add_budget
    app.add_handler(finman.create_budget_conv_handler) # command : /create_budget
    app.add_handler(finman.create_wallet_conv_handler) # command : /create_wallet
    app.add_handler(finman.create_category_conv_handler) # command : /create_category
    app.add_handler(finman.add_wishlist_conv_handler) # command : /create_wishlist
    app.add_handler(finman.execute_wishlist_conv_handler) # command : /execute_wishlist
    
    #MESSAGE
    # app.add_handler(MessageHandler(filters.TEXT, message_handler))

    #ERROR
    app.add_error_handler(scheduler.error_handler)

    #Startup services
    scheduler.scheduler.SchedulerStart()

    #Polls the bot
    print("Polling...")
    app.run_polling(poll_interval=0.5)