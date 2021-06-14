#Intermediary between citation_scraper.py, to later allow caching
from source import citation_scraper

def get_citation(URL):
    return citation_scraper.get_URL_text(URL)