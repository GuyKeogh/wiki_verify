"""
__description__ = "Extracts plaintext from external link URL"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

import re
import requests
from bs4 import BeautifulSoup    
from source import __metadata__

def generate_header(language="", article_title=""):
    """Creates the HTTP header which is sent when requesting citations"""
    header = {
        'User-Agent': 'wiki_verify/'+__metadata__.__VERSION__,
        'Accept-Language': "en-US,en;q=0.5",
        'referer': "https://"+language+".wikipedia.org/"+article_title.replace(" ", "_"),
        'UPGRADE-INSECURE-REQUESTS': "1",
        'Save-Data': "on",
        }
    if __metadata__.__IF_WEB__: #Don't need to link to the site if it's locally hosted
        header.__setitem__('Host', 'https://verify.toolforge.org/')
    return header

def get_URL_text(URL,headers,if_ignore_URL_error=True):
    """Get the HTML from the page, strip the tags, and output the bare text"""
    try:
        res = requests.get(URL, headers=headers, timeout=5, allow_redirects=True)
        try:
            res.raise_for_status() #Fails if error occurs, which is caught as an exception

            html_page = res.content
            parsed_html = BeautifulSoup(html_page,'html.parser')
            text = parsed_html.find_all(text=True)

            plain_text = remove_junk(text)
            return plain_text
        except Exception as exc:
            if not if_ignore_URL_error:
                print('There was a problem: %s' % (exc))
            return "404"
    except Exception as exc:
        if not if_ignore_URL_error:
            print('There was a problem requesting the URL: %s' % (exc))

def remove_junk(text):
    """Get rid of HTML and script tags in the citation text"""
    output = ''
    #Rm tags and scripts
    word_blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head', 
        'input',
        'script',
        'footer',
        'style',
    ]  

    for word in text:
        if word.parent.name not in word_blacklist:
            output += '{} '.format(word)

    #Strip tabs, newlines, etc
    output = re.sub(r'(^[ \t]+|[ \t]+(?=:))', '', output, flags=re.M)
    output = " ".join(output.split())

    return output.strip()
