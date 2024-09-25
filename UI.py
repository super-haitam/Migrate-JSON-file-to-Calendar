from datetime import datetime
import os
from main import createEvent, getDictfromJson, processDictToEventsList, calName_id_dict, eventDateToDt
from utils import getCreds

def welcome():
    print("Welcome. This is a script that given a JSON file, add events into the Google Calendar via its API.")
    print("""
    The JSON file needs to meet the following requirements:
        {
          "(DAY DATE MONTH)":[
            {
                "startTime": "(HH)H(MM)", 
                "endTime": "(HH)H(MM)", 
                "lesson": "(Lesson)", 
                "location": "(Location)",
                "number": "(Number)",
                "notice": "(Notice)"
            },
            ...
          ],
          ...
        }
""")
    year = int(input("But first, what YEAR are you in: "))
    filepath = input("Please type the path to the JSON file: ")
    
    # Calendar
    print("Now, let's choose the calendar: ")
    for i, calendar in enumerate(list(calName_id_dict.keys())):
        print(f"\t{i+1}. {calendar}")
    calNum = int(input())
    calendarName = list(calName_id_dict.keys())[ calNum - 1 ]

    # Start Date
    start_from_date = False
    if input("Do you want to start from a specific date? (y/n): ").lower() == "y":
        d = input("Type it: (HH:MM:SS - DD/MM/YYYY) ").split(' - ')
        d_colon = [int(i) for i in d[0].split(':')]
        d_slash = [int(i) for i in d[1].split('/')]
        dt = datetime(d_slash[2], d_slash[1], d_slash[0], d_colon[0], d_colon[1])
        start_from_date = True

    # Check if the path is valid
    if not os.path.exists(filepath):
        raise ValueError("No such file or directory: " + filepath)
    
    data = getDictfromJson(filepath)
    pData = processDictToEventsList(data, year)

    for i, event in enumerate(pData):
        if not start_from_date or (start_from_date and dt <= eventDateToDt(event["startDate"])):
            createEvent(
                getCreds(),
                calendarName,
                event["summary"],
                event["startDate"],
                event["endDate"],
                event["description"],
                event["location"]
            )

        print(f"{i+1} Events Created. We are now {((i+1)/len(pData))*100:.2f}% complete!")
    

if __name__ == "__main__":
    welcome()