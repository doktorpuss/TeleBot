import secrete
from telegram import Update
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes

serving = False

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global serving

    # start tasks programable
    await update.message.reply_text("I'm ready. What can I help you?")

async def end_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # end tasks programable
    await update.message.reply_text("Copied. Call me whenever you want.")

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

    #MESSAGE
    app.add_handler(MessageHandler(filters.TEXT, message_handler))

    #ERROR
    app.add_error_handler(error)

    #Polls the bot
    print("Polling...")
    app.run_polling(poll_interval=0.5)