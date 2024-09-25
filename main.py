from datetime import datetime
import utils
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Credentials
creds = utils.getCreds()

# Calendars
calName_id_dict = utils.getCalNametoIdDict(creds)


def getDictfromJson(filepath: str) -> dict:
    with open(filepath, 'r') as f:
        data = json.load(f)

    return data

def eventDateToDt(date: str) -> datetime:
    day = date.split('T')[0]
    time = date.split('T')[1]

    year = int(day.split('-')[0])
    month = int(day.split('-')[1])
    day = int(day.split('-')[2])

    hour = int(time.split(':')[0])
    minute = int(time.split(':')[1])

    return datetime(year, month, day, hour, minute)

def getEmoji(text: str):
    wordEmoji = {
        "chimie": '🧪',
        "mécanique": '🚀',
        "logiciel,python,computing": '🖥️',
        "anglais": '🇬🇧',
        "français": '🇫🇷',
        "optique": '🔎',
        "langue": '🗣️',
        "travail": '📝',
        "analyse": '📈',
        "algèbre": '🔢'
    }

    for words in wordEmoji:
        for word in words.split(','):
            if word in text.lower():
                return wordEmoji[words]
    
    raise ValueError(f"Not found emoji for " + text)

def processDictToEventsList(data: dict, year: int) -> dict:
    dataList = []

    # Month to number dict
    monthToNumStr = {
        "Janvier": "01",
        "Février": "02",
        "Mars": "03",
        "Avril": "04",
        "Mai": "05",
        "Juin": "06",
        "Juillet": "07",
        "Août": "08",
        "Septembre": "09",
        "Octobre": "10",
        "Novembre": "11",
        "Décembre": "12"
    }


    for date in data:
        dateL = date.split(' ')
        day = dateL[1]
        month = monthToNumStr[dateL[2]]

        assert len(day) == 2

        for timeSlot in data[date]:
            start = timeSlot["startTime"].split("H")
            end = timeSlot["endTime"].split("H")
            lesson = timeSlot["lesson"]
            location = timeSlot["location"]
            number = timeSlot["number"]
            notice = timeSlot["notice"]

            number_formatted = '\t' + str(number) if isinstance(number, int) else '\t' + "\n\t".join(str(number).split("\n"))
            notice_formatted = '\t' + "\n\t".join(notice.split("\n"))

            dataList.append( 
                {
                "startDate": f"{year}-{month}-{day}T{start[0]}:{start[1]}:00+01:00",
                "endDate": f"{year}-{month}-{day}T{end[0]}:{end[1]}:00+01:00",
                "summary": getEmoji(lesson) + " " + lesson,
                "description": f"Number:\n{number_formatted}\n\nNotice:\n{notice_formatted}",
                "location": location
                }
            )

    return dataList

def createEvent(creds: Credentials, calendarName: str, summary: str, startDate: str, endDate: str, description: str, location: str) -> None:
    """
        Create a new event based on the passed values.
    """
    if calendarName != "primary" and calendarName not in calName_id_dict:
        raise ValueError(f"The calendar name specified is not valid. Must be one of {list(calName_id_dict.keys())}")

    try:
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {
                "dateTime": startDate,
                "timeZone": "Africa/Casablanca"
            },
            "end": {
                "dateTime": endDate,
                "timeZone": "Africa/Casablanca"
            }
        }

        assert calendarName in calName_id_dict
        
        event = service.events().insert(
            calendarId=calName_id_dict[calendarName], 
            body=event
            ).execute()

    except HttpError as error:
        print(f"An error occurred {error}")


