"""
__description__ = "Internal information about the program"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

__IF_PRODUCTION__ = True
__VERSION__ = "0.9.0"
CORRECTION_RETENTION_TIME = 30 #Minutes
__IF_WEB__ = False
__WEB_EXTERNAL_URL_LIMIT__ = 100

#Don't auto-scrape these URLs, and instead ask for copy-and-paste:
__DO_NOT_SCRAPE_URLS__ = ["web.archive.org/web/",
                          "archive.is/"]
