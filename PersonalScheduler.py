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
                        end = event['end'].get('dateTime', event['end'].get('date'))
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



