from datetime import timedelta
from colorama import Fore,Back,Style
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

creds = None
service = None

region = 'vi'
# region = 'gb'  # Global format

previous_date_dict = None

VietnamPeriod = {
    "Morning":"Sáng",
    "Afternoon":"Trưa",
    "Evening":"Chiều",
    "Night":"Tối",
    "Mid night":"Đêm",
    "Full day":"Cả ngày"
}

VietnamWeekDay = {
    "Mon":"Thứ hai",
    "Tue":"Thứ ba",
    "Wed":"Thứ tư",
    "Thu":"Thứ năm",
    "Fri":"Thứ sáu",
    "Sat":"Thứ bảy",
    "Sun":"Chủ nhật"
}

GlobalWeekDay = {
    "Mon":"Monday",
    "Tue":"Tuesday",
    "Wed":"Wednesday",
    "Thu":"Thursday",
    "Fri":"Friday",
    "Sat":"Saturday",
    "Sun":"Sunday"
}

VietnamMonth = {
    "Jan":"Tháng 1",
    "Feb":"Tháng 2",
    "Mar":"Tháng 3",
    "Apr":"Tháng 4",
    "May":"Tháng 5",
    "Jun":"Tháng 6",
    "Jul":"Tháng 7",
    "Aug":"Tháng 8",
    "Sep":"Tháng 9",
    "Oct":"Tháng 10",
    "Nov":"Tháng 11",
    "Dec":"Tháng 12"
}

GlobalMonth = {
    "Jan":"January",
    "Feb":"Febuary",
    "Mar":"March",
    "Apr":"April",
    "May":"May",
    "Jun":"June",
    "Jul":"July",
    "Aug":"August",
    "Sep":"September",
    "Oct":"October",
    "Nov":"November",
    "Dec":"December"
}

def today():
    date = datetime.datetime.now()
    date = date.__str__().split()[0]
    return datetime.datetime.fromisoformat(date)    

def DateTime_to_TimeDict(dt:datetime): 
    date,time = dt.__str__().split()
    date = date.split('-')

    timezone = "00:00"

    if '+' in time:
        time,timezone = time.split('+')
    time = time.split(':')

    #period
    time_int = int(time[0])
    if (time_int >= 3) and (time_int < 11): period = "Morning"
    elif (time_int >= 11) and (time_int < 14): period = "Afternoon"
    elif (time_int >= 14) and (time_int < 19): period = "Evening"
    elif (time_int >= 19) and (time_int < 24): period = "Night"
    elif (time_int > 0) and (time_int < 3): period = "Mid night"
    else : period = "Full day"

    if region == 'vi':
        weekday = VietnamWeekDay[dt.ctime().split()[0]]
        period = VietnamPeriod[period]
    else :
        weekday = GlobalWeekDay[dt.ctime().split()[0]]

    date_value = (int(date[2]) + int(date[1]) * 31 + int(date[0]) * 31 * 12)*10000 + int(time[0])*60 + int(time[1])

    dt_dict = {
        "weekday": weekday,
        "day": date[2],
        "month": date[1],
        "year": date[0],
        "hour": time[0],
        "minute": time[1],
        "second": time[2],
        "period": period,
        "timezone": timezone,
        "date_value": date_value
    }

    return dt_dict

def MakeEventDict(event,cal_name):
    start = event['start'].get('dateTime', event['start'].get('date'))
    start = datetime.datetime.fromisoformat(start)
    start = DateTime_to_TimeDict(start)
    start_str = f"{start['hour']}:{start['minute']}"

    end = event['end'].get('dateTime', event['end'].get('date'))
    end = datetime.datetime.fromisoformat(end)
    end = DateTime_to_TimeDict(end)
    end_str = f"{end['hour']}:{end['minute']}"

    summary = event.get('summary','No Title')
    print(f"\t[{start_str} ---> {end_str}]: {event.get('summary', 'No Title')}\n")

    return {
        "start": start,
        "start_str": start_str,
        "end": end,
        "end_str": end_str,
        "summary": summary,
        "cal_name": cal_name
    }


def SchedulerStart():
    global creds,service

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token/token.json"):
        creds = Credentials.from_authorized_user_file("token/token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "token/CalendarCredential.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar","v3",credentials=creds)

        # now = datetime.datetime.now().isoformat() + "Z"
        # end = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() + "Z"

        # # Get calendar list 
        # calendar_list = service.calendarList().list().execute()

        # print("2-----------------------------")

        # for calendar_entry in calendar_list['items']:
        #     cal_id = calendar_entry['id']
        #     cal_name = calendar_entry['summary']
        #     print(f"\n--- Lịch: {cal_name} ---")

        #     events_result = service.events().list(
        #         calendarId=cal_id,
        #         timeMin=now,
        #         timeMax=None,
        #         maxResults=10,
        #         singleEvents=True,
        #         orderBy="startTime",
        #     ).execute()

        #     events = events_result.get('items', [])

        #     if not events:
        #         print("No upcoming events found.")
        #         return
            
        #     for event in events:
        #         start = event['start'].get('dateTime', event['start'].get('date'))
        #         end = event['end'].get('dateTime', event['end'].get('date'))
        #         print(f"[{start} ---> {end} ]: {event.get('summary', 'No Title')}")

    except HttpError as error:
        print(f"An error occurred: {error}")

def check_prev_date(date_dict):
    global previous_date_dict

    flag = False

    if previous_date_dict == None:
        previous_date_dict = date_dict
        flag = True
    elif (previous_date_dict['day'] != date_dict['day']) or (previous_date_dict['month'] != date_dict['month']) or (previous_date_dict['year'] != date_dict['year']):
        previous_date_dict = date_dict
        flag = True
    
    ret_str = ""

    if flag:
        ret_str = f"\n[ {date_dict['weekday']}, Ngày {date_dict['day']}/{date_dict['month']}/{date_dict['year']} ]:\n"

    return ret_str
    


def GetEvents(start_time=None, end_time=None, num: int = 2500, CalList = None):
    global service,previous_date_dict

    try:
        result: str = ""
        
        # Get calendar list 
        calendar_list = service.calendarList().list().execute()

        # Resolve Null start_time
        if not start_time:
            start_time = datetime.datetime.now()

        if not end_time:
            end_time = start_time + timedelta(days=1)

        # Resolve Null Calist:
        if not CalList:
            CalList = []
            for calendar_entry in calendar_list['items']:
                CalList.append(calendar_entry['summary'])

        print(Style.BRIGHT)

        # Get requested
        events_list = []
        for calendar_demanded in CalList:
            for calendar_entry in calendar_list['items']:
                if (calendar_demanded == calendar_entry['summary']):
                    cal_id = calendar_entry['id']
                    cal_name = calendar_entry['summary']
                    print(Fore.GREEN + "Kiểm tra lịch" + Fore.BLUE + f"[{cal_name}]:" + Fore.RESET )

                    events_result = service.events().list(
                        calendarId=cal_id,
                        timeMin=start_time.isoformat() + "Z",
                        timeMax=end_time.isoformat() + "Z",
                        maxResults=num,
                        singleEvents=True,
                        orderBy="startTime",
                    ).execute()

                    events = events_result.get('items', [])

                    if not events:
                        print(Fore.MAGENTA +"No upcoming events found." + Fore.RESET)
                        continue
                    
                    for event in events:

                        e_dict = MakeEventDict(event,cal_name)
                        events_list.append(e_dict)  
        
        #sort event
        events_list.sort(key = lambda x: x["start"]["date_value"])

        # print events
        previous_date_dict = None
        for event in events_list:
            # result = result + check_prev_date(event['start']) + f"\t{event['start_str']} -> {event['end_str']}: {event['summary']} \n"
            result = result + check_prev_date(event['start']) + f"\t[{event['start_str']} ---> {event['end_str']}]: {event['summary']} \t({event['start']['period']})\n"
            # result = result + check_prev_date(event['start']) + f"\t[{event['start_str']} ---> {event['end_str']}]: {event['summary']} \t({event['cal_name']})\n"

        if result == "":
            result = f"Không có sự kiện nào từ ngày {start_time} đến ngày {end_time}"

        print("\n" + Fore.YELLOW + f"result: \n{result}" + Fore.RESET)
        return result
        
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    SchedulerStart()

    # start = datetime.datetime.fromisoformat('2025-08-31')
    start = today()
    # end = start + timedelta(days=2)
    # output = GetEvents(start_time = start, end_time = end)
    output = GetEvents(start_time = start)

    print("\n================================================")
    print("OUTPUT:")
    print(output)



