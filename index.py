import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import schedule 
import time
import smtplib
import datetime 
from config import user_email,user_password
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def fetch_birthdays():
# GOOGLE CALENDAR CODE
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='addressbook#contacts@group.v.calendar.google.com',alwaysIncludeEmail=True, timeMin=now,
                                        maxResults=1, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return False
    # start = events['start'].get('dateTime', events['start'].get('date'))
    return events



def birthDay():
    d=datetime.date.today()
    events=fetch_birthdays()
    if events:
        for event in events:
            start_date=event['start'].get('dateTime', event['start'].get('date'))
            if start_date==d:
                to_email=event['gadget']['preferences']['goo.contactsEmail']
                to_name=event['gadget']['preferences']['goo.contactsFullName']
                sendEmail(to_email=to_email,to_name=to_name)
 
def sendEmail(to_email,to_name):
    message="""
        Subject: Happy Birthday %s!
        
        Many Happy Returns of the day!

        From,
        Lakshya Khera
        Web Developer
    """% (to_name) 
    # Don't Forget to change the name!
    try:  
        server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server_ssl.login(user_email, user_password)
        server_ssl.sendmail("lakshya.khera@gmail.com",to_email,message)
        server_ssl.close()
        print("Email sent")
    except:  
        print ('Something went wrong...')


if __name__ == '__main__':
    schedule.every().day.at("00:00").do(birthDay)
    while True:
        schedule.run_pending() 
        time.sleep(1) 
    