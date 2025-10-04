import datetime
import secrete
from colorama import Fore,Back,Style
from telegram import Update
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes,ConversationHandler

from . import PersonalScheduler as scheduler

ndayinmonth = [31,28,31,30,31,30,31,31,30,31,30,31]

serving = False


#utilities

def replace_date_ref_by_exact_date(text):
    # Arguments handler
    text = text.lower()
    if ("today" in text):
        today = datetime.datetime.now().__str__().split()[0]
        text = text.replace("today",today)
    elif ("hôm nay" in text):
        today = datetime.datetime.now().__str__().split()[0]
        text = text.replace("hôm nay",today)
    elif ("nay" in text):
        today = datetime.datetime.now().__str__().split()[0]
        text = text.replace("nay",today)
    
    if ("tomorrow" in text):
        tormorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).__str__().split()[0]
        text = text.replace("tomorrow",tormorrow)
    elif ("ngày mai" in text):
        tormorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).__str__().split()[0]
        text = text.replace("ngày mai",tormorrow)
    elif ("mai" in text):
        tormorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).__str__().split()[0]
        text = text.replace("mai",tormorrow)

    if ("the day before" in text):
        day_before = (datetime.datetime.now() - datetime.timedelta(days=1)).__str__().split()[0]
        text = text.replace("the day before",day_before)
    elif ("hôm qua" in text):
        day_before = (datetime.datetime.now() - datetime.timedelta(days=1)).__str__().split()[0]
        text = text.replace("hôm qua",day_before)

    return text

def reaplace_daypart_by_exact_time(text):
    if ("morning" in  text):
        text = text.replace("morning","08:00|11:00")
    elif ("sáng"in  text):
        text = text.replace("sáng","08:00|11:00")
    
    if ("afternoon" in  text):
        text = text.replace("afternoon","12:00|13:00")
    elif ("trưa"in  text):
        text = text.replace("trưa","12:00|13:00")

    if ("evening" in  text):
        text = text.replace("evening","14:00|18:00")
    elif ("chiều"in  text):
        text = text.replace("chiều","14:00|18:00")

    if ("night" in  text):
        text = text.replace("night","20:00|23:00")
    elif ("tối" in  text):
        text = text.replace("tối","20:00|23:00")

    return text


def extract_date_time_from_text(text) :
    text = text.split()
    if (len(text)==1):
        if ('/' in text[0]) or ('-' in text[0]):
            return text[0],""
        if (':' in text[0]):
            return "",text[0]
    elif (len(text)==2):
        if (':' in text[0]) and (('/' in text[1]) or ('-' in text[1])):
            return text[1],text[0]
        elif (':' in text[1]) and (('/' in text[0]) or ('-' in text[0])):
            return text[0],text[1]
    return "",""

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

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


# GET EVENT 

# conversation states
GET_EVENT_START = "GET_EVENT_START"
ASK_TIME_RANGE = "ASK_TIME_RANGE"

# def get_event_process(text):

#     if text == "":
#         response = scheduler.GetEvents()
#         return response
        
#     text = replace_date_ref_by_exact_date(text)

#     text = text.split()
#     if (len(text)==1):
#         text[0] = scheduler.normalize_date_string(text[0])
#         print(Fore.RED + text[0] + Fore.RESET)
#         start = datetime.datetime.fromisoformat(text[0])
#         response = scheduler.GetEvents(start_time = start)
#         return response
        
#     elif (len(text)==3):
#         text[0] = scheduler.normalize_date_string(text[0])
#         text[2] = scheduler.normalize_date_string(text[2])
#         print(Fore.RED + text[0] + " to " + text[2] + Fore.RESET)
#         start = datetime.datetime.fromisoformat(text[0])
#         end = datetime.datetime.fromisoformat(text[2])
#         response = scheduler.GetEvents(start_time = start, end_time = end)
#         return response

def get_event_process(text):
        
    text = replace_date_ref_by_exact_date(text)
    text = reaplace_daypart_by_exact_time(text)

    if "to" in text:
        text = text.split(" to ")
    elif "đến" in text:
        text = text.split(" đến ")
    elif ('/' in text) or ('-' in text) or (':' in text):
        text = [text,""]
    else:
        return "Vui lòng nhập đúng định dạng: <thời gian bắt đầu> đến/to <thời gian kết thúc>\n <ngày muốn kiểm tra>"
    
    start_date,start_time = extract_date_time_from_text(text[0])
    end_date,end_time = extract_date_time_from_text(text[1])

    if start_date == "" : start_date = datetime.datetime.now().__str__().split()[0]
    if '/' in start_date: start_date = scheduler.normalize_date_string(start_date)
    if '/' in end_date: end_date = scheduler.normalize_date_string(end_date)

    if ("|" in start_time):
        if not ("|" in end_time): 
            end_time = start_time.split("|")[1]   
            start_time = start_time.split("|")[0]
        elif ("|" in end_time): 
            end_time = end_time.split("|")[1]
            start_time = start_time.split("|")[0]


    print (Fore.LIGHTYELLOW_EX + start_date + " " + start_time + " to " + end_date + " " + end_time + Fore.RESET)
    # full info
    if (end_date != "") and (end_time != "") and (start_time != ""):
        start = datetime.datetime.fromisoformat(start_date + " " + start_time)
        end = datetime.datetime.fromisoformat(end_date + " " + end_time)
        response = scheduler.GetEvents(start_time = start, end_time = end)
        return response
    
    # date only
    if (end_date == "") and (end_time == "") and (start_time == ""):
        start = datetime.datetime.fromisoformat(start_date)
        response = scheduler.GetEvents(start_time = start)
        return response
    
    #inday timerange range
    if (end_date == "") and (end_time != "") and (start_time != ""):
        start = datetime.datetime.fromisoformat(start_date + " " + start_time)
        end = datetime.datetime.fromisoformat(start_date + " " + end_time)    
        response = scheduler.GetEvents(start_time = start, end_time = end)
        return response
    
    return "Vui lòng nhập đúng định dạng: <thời gian bắt đầu> đến/to <thời gian kết thúc>\n <ngày muốn kiểm tra>"

# async def get_event_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # Ưu tiên lấy message từ update.message, nếu không có thì lấy từ update.edited_message
#     message = update.message or update.edited_message
#     if not message or not message.text:
#         await update.message.reply_text("Không dùng Edit message")
#         print("Edit message, không xử lý")
#         return  # bỏ qua update không có text
    
#     text = message.text.replace("/event", "").strip()
#     print(f"got text: {text}\n")

#     response = get_event_process(text)

#     await update.message.reply_text(response)
#     return ASK_TIME_RANGE

async def get_event_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Get event process start")

    await update.message.reply_text("Hãy cho tôi biết khoảng thời gian bạn muốn kiểm tra:")
    await update.message.reply_text("Hãy nhập theo định dạng: \"<date> <time>to/đến <date> <time>\" \nor \"<date>\"")
    return ASK_TIME_RANGE

async def ask_time_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = get_event_process(text)
    await update.message.reply_text(response)
    if response == "Vui lòng nhập đúng định dạng: <thời gian bắt đầu> đến/to <thời gian kết thúc>\n <ngày muốn kiểm tra>":
        return ASK_TIME_RANGE
    return ConversationHandler.END

async def CMD_today_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = scheduler.GetEvents()
    await update.message.reply_text(response)

async def CMD_week_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    week_start = scheduler.today() - datetime.timedelta(days=datetime.datetime.now().weekday())
    week_end = week_start + datetime.timedelta(days=7)

    response = scheduler.GetEvents(start_time=week_start, end_time=week_end)
    await update.message.reply_text(response)

async def CMD_month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    month_start = datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().day)
    month_end = month_start + datetime.timedelta(days=ndayinmonth[datetime.datetime.now().month-1])

    response = scheduler.GetEvents(start_time=month_start, end_time=month_end)
    await update.message.reply_text(response)
# END GET EVENT



# CREATE EVENT

#Conversation states:
ASK_START_TIME = "ASK_START_TIME"
ASK_END_TIME = "ASK_END_TIME"
ASK_SUMARY = "ASK_SUMARY"
ASK_OPTIONS = "ASK_OPTIONS"
ASK_CONFIRM = "ASK_CONFIRM"
CREATE_EVENT = "CREATE_EVENT"

# create_event_info packages in below format:
# create_event_info = [start_time, end_time, summary, options]
# all string elements
# options is string with multiple option seperated by comma, example:"option1_name: option1_value, option2_name: option2_value, ..." 
# create_event_info filled by 

class EventInfo:
    start_time = ""
    end_time = ""
    end_date = ""
    start_date = ""
    summary = ""
    options = ""
    CalID = "primary"

    def reset(self):
        self.start_time = ""
        self.end_time = ""
        self.end_date = ""
        self.start_date = ""
        self.summary = ""
        self.options = ""
        self.CalID = "primary"

create_event_info = EventInfo()

async def ask_event_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Create event process start")
    await update.message.reply_text("Hãy cho tôi biết thời điểm bắt đầu:")
    create_event_info.reset()
    return ASK_START_TIME

async def ask_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    text = replace_date_ref_by_exact_date(text)

    # #if daypart included
    temp = reaplace_daypart_by_exact_time(text)
    if (temp != text):
        text = temp.split()
        if (len(text)==1):
            create_event_info.start_date = scheduler.today().__str__().split()[0]
            create_event_info.end_date = create_event_info.start_date
            create_event_info.start_time = text[0].split('|')[0]
            create_event_info.end_time = text[0].split('|')[1]
            await update.message.reply_text("Hãy cho tôi biết tên của sự kiện:")
            return ASK_SUMARY
        elif (len(text)==2):
            if (('/' in text[0]) or ('-' in text[0])) and (':' in text[1]):
                create_event_info.start_date = text[0]
                create_event_info.start_time = text[1].split('|')[0]
                create_event_info.end_date = text[0]
                create_event_info.end_time = text[1].split('|')[1]
                await update.message.reply_text("Hãy cho tôi biết tên của sự kiện:")
                return ASK_SUMARY
            elif (':' in text[0]) and (('/' in text[1]) or ('-' in text[1])):
                create_event_info.start_date = text[1]
                create_event_info.start_time = text[0].split('|')[0]
                create_event_info.end_date = text[1]
                create_event_info.end_time = text[0].split('|')[1]
                await update.message.reply_text("Hãy cho tôi biết tên của sự kiện:")
                return ASK_SUMARY
        
        await update.message.reply_text("Không đúng định dạng thời gian. \nXin hãy nhập lại hoặc /cancel để bỏ qua")
        return ASK_START_TIME

    # if not daypart included
    text = text.split()
    
    print(len(text))
    for t in text:
        print(Fore.RED + t + Fore.RESET)

    print(text)

    if(len(text) == 1):
        # only date means full day event
        if ('/' in text[0]) or ('-' in text[0]):
            create_event_info.start_date = text[0]
            await update.message.reply_text("Hãy cho tôi biết tên của sự kiện:")
            return ASK_SUMARY
        #only time mean start_date is today but at specific time
        elif ':' in text[0]:
            create_event_info.start_date = scheduler.today().__str__().split()[0]
            create_event_info.start_time = scheduler.normalize_time_string(text[0])
            await update.message.reply_text("Hãy cho tôi biết thời điểm kết thúc:")
            return ASK_END_TIME 
        else:
            await update.message.reply_text("Không đúng định dạng thời gian. \nXin hãy nhập lại hoặc /cancel để bỏ qua")
            return ASK_START_TIME
    elif(len(text) == 2):
        if (('/' in text[0]) or ('-' in text[0])) and (':' in text[1]):
            create_event_info.start_date = text[0]
            create_event_info.start_time = scheduler.normalize_time_string(text[1])
            await update.message.reply_text("Hãy cho tôi biết thời điểm kết thúc:")
            return ASK_END_TIME 
        elif (':' in text[0]) and (('/' in text[1]) or ('-' in text[1])):
            create_event_info.start_time = scheduler.normalize_time_string(text[0])
            create_event_info.start_date = text[1]
            await update.message.reply_text("Hãy cho tôi biết thời điểm kết thúc:")
            return ASK_END_TIME 
        else:
            await update.message.reply_text("Không đúng định dạng thời gian. \nXin hãy nhập lại hoặc /cancel để bỏ qua")
            return ASK_START_TIME
        
    await update.message.reply_text("Không đúng định dạng thời gian. \nXin hãy nhập lại hoặc /cancel để bỏ qua")
    return ASK_START_TIME

async def ask_event_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    text = replace_date_ref_by_exact_date(text)
    text = text.split()

    if(len(text) == 1):
        # only date means full day event
        if ('/' in text[0]) or ('-' in text[0]):
            create_event_info.end_date = text[0]
            await update.message.reply_text("Hãy cho tôi biết tên của sự kiện:")
            return ASK_SUMARY
        #only time meann end_date the same as start_date but at specific time
        elif ':' in text[0]:
            create_event_info.end_date = create_event_info.start_date
            create_event_info.end_time = scheduler.normalize_time_string(text[0])
            await update.message.reply_text("Hãy cho tôi biết tên của sự kiện:")
            return ASK_SUMARY 
        else:
            await update.message.reply_text("Không đúng định dạng thời gian. \nXin hãy nhập lại hoặc /cancel để bỏ qua")
            return ASK_END_TIME
    elif(len(text) == 2):
        if (('/' in text[0]) or ('-' in text[0])) and (':' in text[1]):
            create_event_info.end_date = text[0]
            create_event_info.end_time = scheduler.normalize_time_string(text[1])
            await update.message.reply_text("Hãy cho tôi biết tên của sự kiện:")
            return ASK_SUMARY 
        elif (':' in text[0]) and (('/' in text[1]) or ('-' in text[1])):
            create_event_info.end_time = scheduler.normalize_time_string(text[0])
            create_event_info.end_date = text[1]
            
            await update.message.reply_text("Hãy cho tôi biết tên của sự kiện:")
            return ASK_SUMARY 
        else:
            await update.message.reply_text("Không đúng định dạng thời gian. \nXin hãy nhập lại hoặc /cancel để bỏ qua")
            return ASK_END_TIME

async def ask_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    create_event_info.summary = text


    create_event_info.start_date = scheduler.normalize_date_string(create_event_info.start_date)

    if create_event_info.end_date != "":
        create_event_info.end_date = scheduler.normalize_date_string(create_event_info.end_date)

    await update.message.reply_text(f"Xác nhận lịch sự kiện mới: \n{create_event_info.start_date} {create_event_info.start_time}, {create_event_info.end_date} {create_event_info.end_time}, {create_event_info.summary}, {create_event_info.options}")
    await update.message.reply_text("Bạn có thể xác nhận, từ bỏ, hoặc cung cấp thêm thông tin \n/oke: Xác nhận \n/cancel: Bỏ tạo sự kiện\n ")
    await update.message.reply_text("Các thông tin bổ sung có thể dung cấp:\n CalID: <tên lịch>")

    return ASK_OPTIONS

async def ask_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    opt_text = text.split(',')

    valid_opt = False

    for opt in opt_text:
        if "CalID: " in opt:
            create_event_info.CalID = text[7:]
            valid_opt = True
        
    if valid_opt:
        await update.message.reply_text(f"Xác nhận lịch sự kiện mới: \n{create_event_info.start_date} {create_event_info.start_time},{create_event_info.end_date} {create_event_info.end_time}, {create_event_info.summary}, {create_event_info.options}")
        await update.message.reply_text("Bạn có thể xác nhận, từ bỏ, hoặc cung cấp thêm thông tin \n/oke: Xác nhận \n/cancel: Bỏ tạo sự kiện\n ")
        await update.message.reply_text("Các thông tin bổ sung có thể dung cấp:\n CalID: <tên lịch>")
        return ASK_OPTIONS
    
    await update.message.reply_text("Hãy nhập thông tin đúng định dạng hoặc /cancel")
    return ASK_OPTIONS
        
async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("CANCELED")
    return ConversationHandler.END

async def create_event_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if create_event_info.end_date == "":
        time_range = create_event_info.start_date
    else:
        time_range = f"{create_event_info.start_date} {create_event_info.start_time} to {create_event_info.end_date} {create_event_info.end_time}"
    sumary = create_event_info.summary
    CalID = create_event_info.CalID

    # create event
    created_event = scheduler.create_event(sumary, time_range, CalID)
    if created_event:
        await update.message.reply_text("✅ Tạo sự kiện thành công")
        return ConversationHandler.END

creat_event_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_event', ask_event_info)],
    states={
        ASK_START_TIME: [MessageHandler(filters.TEXT & ~ filters.COMMAND, ask_event_start)],
        ASK_END_TIME: [MessageHandler(filters.TEXT & ~ filters.COMMAND, ask_event_end)],
        ASK_SUMARY: [MessageHandler(filters.TEXT & ~ filters.COMMAND, ask_summary)],
        ASK_OPTIONS: [MessageHandler(filters.TEXT & ~ filters.COMMAND, ask_options),CommandHandler('oke', create_event_handler),],

    },
    fallbacks=[CommandHandler('cancel', cancel_handler)],
)

get_event_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('event', get_event_handler)],
    states={ 
        ASK_TIME_RANGE: [MessageHandler(filters.TEXT & ~ filters.COMMAND, ask_time_range)],
    },
    fallbacks=[CommandHandler('cancel', cancel_handler)],
)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Error: {context.error}")

    # Nếu có update và là tin nhắn
    if update and getattr(update, "message", None):
        await update.message.reply_text("⚠️ Lỗi: " + str(context.error))
    elif update and getattr(update, "callback_query", None):
        await update.callback_query.message.reply_text("⚠️ Lỗi: " + str(context.error))
    else:
        # Trường hợp lỗi hệ thống (ví dụ network), không gửi cho user
        print("Lỗi hệ thống, không gửi thông báo cho user.")