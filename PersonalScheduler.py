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

def DateTime_to_TimeDict(dt:datetime): 
    date,time = dt.__str__().split()
    date = date.split('-')
    time,timezone = time.split('+')
    time = time.split(':')
    
    if region == 'vi':
        weekday = VietnamWeekDay[dt.ctime().split()[0]]
    else :
        weekday = GlobalWeekDay[dt.ctime().split()[0]]

    dt_dict = {
        "weekday": weekday,
        "day": date[2],
        "month": date[1],
        "year": date[0],
        "hour": time[0],
        "minute": time[1],
        "second": time[2],
        "timezone": timezone
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
        #         print(f"[{start} ---> {end} ]: {event.get("summary", "No Title")}")

    except HttpError as error:
        print(f"An error occurred: {error}")

def GetEvents(start_time=None, end_time=None, num: int = 2500, CalList = None):
    global service

    try:
        result: str = ""
        
        # Get calendar list 
        calendar_list = service.calendarList().list().execute()

        # Resolve Null start_time
        if not start_time:
            start_time = datetime.datetime.now()

        if not end_time:
            end_time = start_time + timedelta(days=30)

        # Resolve Null Calist:
        if not CalList:
            CalList = []
            for calendar_entry in calendar_list['items']:
                CalList.append(calendar_entry['summary'])

        print(Style.BRIGHT)

        # Get requested
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
                    
                    result = result + f"{cal_name}:\n"
                    for event in events:

                        start = event['start'].get('dateTime', event['start'].get('date'))
                        start = datetime.datetime.fromisoformat(start)
                        # start_date,start_time =  

                        end = event['end'].get('dateTime', event['end'].get('date'))
                        end = datetime.datetime.fromisoformat(end)

                        print(f"[{start} ---> {end} ]: {event.get("summary", "No Title")}")
                        result = result + f"[{start} ---> {end} ]: {event.get("summary", "No Title")}\n"
                    
                    result = result + '\n'

        if result == "":
            result = f"Không có sự kiện nào từ ngày {start_time} đến ngày {end_time}"

        print("\n" + Fore.YELLOW + f"result: \n{result}" + Fore.RESET)
        return result
        
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    SchedulerStart()

    # start = datetime.datetime.fromisoformat('2026-03-01')
    start = datetime.datetime.now()
    output = GetEvents(start_time = start)

    print("\n================================================")
    print("OUTPUT:")
    print(output)



