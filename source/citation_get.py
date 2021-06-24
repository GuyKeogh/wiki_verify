"""
__description__ = "Intermediary between citation_scraper.py, to later allow caching"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from source import citation_scraper, __metadata__

def get_citation(URL, header, if_ignore_URL_error=True):
    return citation_scraper.get_URL_text(URL, header, if_ignore_URL_error=if_ignore_URL_error)

def generate_header(language="", article_title=""):
    header = {
            'User-Agent': 'wiki_verify/'+__metadata__.__version__,
            'Accept-Language': "en-US,en;q=0.5",
            'referer': "https://"+language+".wikipedia.org/"+article_title.replace(" ", "_"),
            'UPGRADE-INSECURE-REQUESTS': "1",
            'Save-Data': "on",
        }
    if(__metadata__.__if_web__): #Don't need to link to the site if it's locally hosted
        header.__setitem__('Host', 'https://verify.toolforge.org/')
    return header