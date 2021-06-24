"""
__description__ = "Get information about improvements and server resources that are needed"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from datetime import datetime

ANALYTICS_RETENTION_HOURS = 168 #168hrs = one week
analytics_submits = [0]*ANALYTICS_RETENTION_HOURS #How many article submits have been made
analytics_successes = [0]*ANALYTICS_RETENTION_HOURS #How many articles successfully submitted
analytics_last_hour_written = 0
analytics_initialise_time = datetime.now().replace(minute=0,second=0,microsecond=0)
analytics_total_sessions = 0
analytics_unused_sessions = 0
analytics_total_used_session_time = 0

def analytics_overwrite(hour): #On a new hour, so set what is being written over to zero
    #Note: isn't accurate if last write was longer than the retention_hours
    overwrite_range = []

    global analytics_last_hour_written
    if hour>analytics_last_hour_written:
        for index in range(analytics_last_hour_written, hour):
            overwrite_range.append(index)
    else: #Wraparound of list values
        for index in range(analytics_last_hour_written, ANALYTICS_RETENTION_HOURS):
            overwrite_range.append(index)
        for index in range(0,hour):
            overwrite_range.append(index)
    
    analytics_last_hour_written = hour
    #Do the overwriting:
    for elem in overwrite_range:
        index = (elem+1)%ANALYTICS_RETENTION_HOURS #Ensure list wraparound to prevent out of bounds
        analytics_submits[index] = 0
        analytics_successes[index] = 0

def analytics_hours_since_init():
    #Get time difference, convert to hours, round down, and if over 168 (a week) start overwriting
    hrs_since = int((((datetime.now()-analytics_initialise_time).total_seconds())/3600)//1)
    hour = hrs_since%ANALYTICS_RETENTION_HOURS
    if hour != analytics_last_hour_written:
        analytics_overwrite(hour)
    return hour
