"""
__description__ = "Internal information about the program"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

__IF_PRODUCTION__ = True
__VERSION__ = "0.9.0"
CORRECTION_RETENTION_TIME = 30 #Minutes
__IF_WEB__ = False #Enforces rules to prevent abuse and reduce bandwidth/processing usage
__WEB_EXTERNAL_URL_LIMIT__ = 100

#Don't auto-scrape these URLs, and instead ask for copy-and-paste:
__DO_NOT_SCRAPE_URLS__ = ["web.archive.org/web/", #These tend to be on citations that don't need them, duplicating content.
                          "archive.is/"] #Scraping doesn't work well on these archive sites anyway. Kind of ironic.
