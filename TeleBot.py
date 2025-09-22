import secrete
import TeleBotScheduleUtil as scheduler
from telegram import Update
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes,ConversationHandler

if __name__ == '__main__':
    print("Starting IRI")
    app = Application.builder().token(secrete.TOKEN).build()

    #COMMAND
    app.add_handler(CommandHandler('start',scheduler.start_handler))
    app.add_handler(CommandHandler('end',scheduler.end_handler))
    # app.add_handler(CommandHandler('event',get_event_handler))
    app.add_handler(CommandHandler('today',scheduler.CMD_today_handler))
    app.add_handler(CommandHandler('week',scheduler.CMD_week_handler))
    app.add_handler(CommandHandler('month',scheduler.CMD_month_handler))

    #CONVERSATION
    app.add_handler(scheduler.creat_event_conv_handler)
    app.add_handler(scheduler.get_event_conv_handler)

    #MESSAGE
    # app.add_handler(MessageHandler(filters.TEXT, message_handler))

    #ERROR
    app.add_error_handler(scheduler.error)

    #Startup services
    scheduler.scheduler.SchedulerStart()

    #Polls the bot
    print("Polling...")
    app.run_polling(poll_interval=0.5)