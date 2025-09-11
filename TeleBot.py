import secrete
import datetime
from colorama import Fore,Back,Style
from telegram import Update
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes

import PersonalScheduler as scheduler

ndayinmonth = [31,28,31,30,31,30,31,31,30,31,30,31]

serving = False

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # start tasks programable
    await update.message.reply_text("I'm ready. What can I help you?")

async def end_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # end tasks programable
    await update.message.reply_text("Copied. Call me whenever you want.")

async def get_event_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ưu tiên lấy message từ update.message, nếu không có thì lấy từ update.edited_message
    message = update.message or update.edited_message
    if not message or not message.text:
        return  # bỏ qua update không có text
    
    text = message.text.replace("/event", "").strip()
    print(f"got text: {text}\n")

    if text == "":
        response = scheduler.GetEvents()
        await update.message.reply_text(response)
        return
        
    # Arguments handler
    if ("today" in text):
        today = datetime.datetime.now().__str__().split()[0]
        text = text.replace("today",today)
    elif ("hôm nay" in text):
        today = datetime.datetime.now().__str__().split()[0]
        text = text.replace("hôm nay",today)
    
    if ("tomorrow" in text):
        tormorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).__str__().split()[0]
        text = text.replace("tomorrow",tormorrow)
    elif ("ngày mai" in text):
        tormorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).__str__().split()[0]
        text = text.replace("ngày mai",tormorrow)

    if ("the day before" in text):
        day_before = (datetime.datetime.now() - datetime.timedelta(days=1)).__str__().split()[0]
        text = text.replace("the day before",day_before)
    elif ("hôm qua" in text):
        day_before = (datetime.datetime.now() - datetime.timedelta(days=1)).__str__().split()[0]
        text = text.replace("hôm qua",day_before)

    text = text.split()
    if (len(text)==1):
        text[0] = scheduler.normalize_date_string(text[0])
        print(Fore.RED + text[0] + Fore.RESET)
        start = datetime.datetime.fromisoformat(text[0])
        response = scheduler.GetEvents(start_time = start)
        await update.message.reply_text(response)
        return
    elif (len(text)==3):
        text[0] = scheduler.normalize_date_string(text[0])
        text[2] = scheduler.normalize_date_string(text[2])
        print(Fore.RED + text[0] + " to " + text[2] + Fore.RESET)
        start = datetime.datetime.fromisoformat(text[0])
        end = datetime.datetime.fromisoformat(text[2])
        response = scheduler.GetEvents(start_time = start, end_time = end)
        await update.message.reply_text(response)
        return

    await update.message.reply_text("Unknown format. \nTry again with: \"<date> to/đến <date>\" \nor \"<date>\"")
    return

async def CMD_today_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = scheduler.GetEvents()
    await update.message.reply_text(response)

async def CMD_week_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    week_start = datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday()+1)
    week_end = week_start + datetime.timedelta(days=7)

    response = scheduler.GetEvents(start_time=week_start, end_time=week_end)
    await update.message.reply_text(response)

async def CMD_month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    month_start = datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().day)
    month_end = month_start + datetime.timedelta(days=ndayinmonth[datetime.datetime.now().month-1])

    response = scheduler.GetEvents(start_time=month_start, end_time=month_end)
    await update.message.reply_text(response)

def response_handler(text:str) -> str:
    return text

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    user_id = update.message.chat.id

    print(f"{user_id}: {text} [{message_type}] ")

    if(message_type == 'group'):
        if secrete.BOT_USERNAME in text:
            response = "This bot is unvailable in group"
        else:
            return
    else:
        response = f"You said \"{text}\""

    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} cause error {context.error}")

if __name__ == '__main__':
    print("Starting IRI")
    app = Application.builder().token(secrete.TOKEN).build()

    #COMMAND
    app.add_handler(CommandHandler('start',start_handler))
    app.add_handler(CommandHandler('end',end_handler))
    app.add_handler(CommandHandler('event',get_event_handler))
    app.add_handler(CommandHandler('today',CMD_today_handler))
    app.add_handler(CommandHandler('week',CMD_week_handler))
    app.add_handler(CommandHandler('month',CMD_month_handler))

    #MESSAGE
    app.add_handler(MessageHandler(filters.TEXT, message_handler))

    #ERROR
    app.add_error_handler(error)

    #Startup services
    scheduler.SchedulerStart()

    #Polls the bot
    print("Polling...")
    app.run_polling(poll_interval=0.5)