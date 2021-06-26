"""
__description__ = "Handles sessions, allowing text from URLs which couldn't be downloaded to be manually input"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from datetime import datetime
from source import analytics, __metadata__
#Other:
sessions = []

def check_session_expiration():
    """Checks if sessions are older than the retention time, and if so deletes them."""
    if sessions:
        (session_ID,article_title,data,text_quotes,settings,session_creation_date) = sessions[0]
        minutes_since_creation = (datetime.now() - session_creation_date).total_seconds() / 60.0
        if minutes_since_creation > __metadata__.CORRECTION_RETENTION_TIME:
            sessions.pop(0)
            analytics.unused_sessions+=1 #Take note that the session wasn't put to use
            check_session_expiration() #Keep looping until all expired sessions are deleted
