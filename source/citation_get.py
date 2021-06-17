"""
__description__ = "#Intermediary between citation_scraper.py, to later allow caching"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from source import citation_scraper

def get_citation(URL):
    return citation_scraper.get_URL_text(URL)