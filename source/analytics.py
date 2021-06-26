"""
__description__ = "Get information about improvements and server resources that are needed"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from datetime import datetime

RETENTION_HOURS = 168 #168hrs = one week
hourly_submits = [0]*RETENTION_HOURS #How many article submits have been made
last_hour_written = 0
initialise_time = datetime.now().replace(minute=0,second=0,microsecond=0)
total_sessions = 0
unused_sessions = 0
total_submits = 0
total_used_session_time = 0
total_urls_requested = 0
total_urls_failed = 0

def overwrite(hour): #On a new hour, so set what is being written over to zero
    #Note: isn't accurate if last write was longer than the retention_hours
    overwrite_range = []

    global last_hour_written
    if hour>last_hour_written:
        for index in range(last_hour_written, hour):
            overwrite_range.append(index)
    else: #Wraparound of list values
        for index in range(last_hour_written, RETENTION_HOURS):
            overwrite_range.append(index)
        for index in range(0, hour):
            overwrite_range.append(index)

    last_hour_written = hour
    #Do the overwriting:
    for elem in overwrite_range:
        index = (elem+1)%RETENTION_HOURS #Ensure list wraparound to prevent out of bounds
        hourly_submits[index] = 0

def hours_since_init():
    #Get time difference, convert to hours, round down, and if over 168 (a week) start overwriting
    hrs_since = int((((datetime.now()-initialise_time).total_seconds())/3600)//1)
    hour = hrs_since%RETENTION_HOURS
    if hour != last_hour_written:
        overwrite(hour)
    return hour
