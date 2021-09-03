"""
__description__ = "Extracts plaintext from external link URL"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

import re
import requests
from bs4 import BeautifulSoup
#from source import __metadata__
import __metadata__

def generate_api_header():
    """Creates the HTTP header which is sent when making Wikipedia API calls"""
    if_from_web_text = "from web"
    if not __metadata__.__IF_WEB__:
        if_from_web_text = "from desktop" #If it's locally launched, mention that
    
    header = {
        'User-Agent': 'wiki_verify/'+__metadata__.__VERSION__+"(https://verify.toolforge.org/) "+if_from_web_text,
        'UPGRADE-INSECURE-REQUESTS': "1",
        'Accept-Encoding': "gzip" #gzip preferred by API
        }
    return header
    
def generate_header(language=""):
    """Creates the HTTP header which is sent when requesting citations"""
    if_from_web_text = "from web"
    if not __metadata__.__IF_WEB__:
        if_from_web_text = "from desktop" #If it's locally launched, mention that
    
    header = {
        'User-Agent': 'wiki_verify/'+__metadata__.__VERSION__+"(https://verify.toolforge.org/) "+if_from_web_text,
        'Accept-Language': "en-US,en;q=0.5",
        'referer': "https://"+language+".wikipedia.org/",
        'UPGRADE-INSECURE-REQUESTS': "1",
        'Accept-Encoding': "deflate, gzip;q=1.0, *;q=0.5", #Automatically decompressed by requests
        'Save-Data': "on",
        }
    return header

def download_wikitext(article_title, language):
    import re
    response = requests.get(
    'https://'+language+'.wikipedia.org/w/api.php',
    params={
    'action': 'query',
    'titles': article_title,
    'format': 'json',
    'prop': 'revisions',
    'rvprop': 'content',
    'rvslots': 'main',
    },
    headers = generate_api_header()
    ).json()

    #Get the wikitext from the dictionary:
    wikitext = next(iter(response['query']['pages'].values()))
    wikitext = wikitext['revisions']
    wikitext = wikitext[0]['slots']
    wikitext = wikitext['main']
    wikitext = wikitext['*']

    return wikitext

def download_article(article_title, language):
    """Download the Wikipedia article text and mark safe HTML elements with codes so they remain the same"""
    response = requests.get(
    'https://'+language+'.wikipedia.org/w/api.php',
    params={
    'action': 'query',
    'titles': article_title,
    'format': 'json',
    'prop': 'extracts', #https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bextracts
    'exsectionformat': 'plain',
    },
    headers = generate_api_header()
    ).json()
    page = next(iter(response['query']['pages'].values()))
    html_page = page['extract']
    
    html_page = html_page.replace('<h2>',' _HEADER2START_ ').replace('</h2>',' _HEADER2END_ ').replace('<h3>',
                        ' _HEADER3START_ ').replace('</h3>',' _HEADER3END_ ').replace('<b>',
                        ' _BOLDSTART_ ').replace('</b>',' _BOLDEND_ ').replace("<i>",' _ITALICSTART_ ').replace("</i>",
                        ' _ITALICEND_ ').replace("<p>",' _PARAGRAPHSTART_ ').replace("</p>",' _PARAGRAPHEND_ ')
    parsed_html = BeautifulSoup(html_page, 'html.parser')
    text = parsed_html.get_text()

    return text

def download_external_URLs(article_title, language):
    """Get list of every unique URL in the Wikipedia article"""
    external_link_limit = 500
    if __metadata__.__IF_WEB__:
        external_link_limit = __metadata__.__WEB_EXTERNAL_URL_LIMIT__+1 #+1 so error can be reported if too many
        
    external_URLs = []
    try:
        response = requests.get(
        'https://'+language+'.wikipedia.org/w/api.php',
        params={
        'action': 'query',
        'titles': article_title,
        'format': 'json',
        'prop': 'extlinks', #https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bextlinks
        'ellimit': str(external_link_limit),
        },
        headers = generate_api_header()
        ).json()
        page = next(iter(response['query']['pages'].values()))
        extracted_page = page['extlinks']
        
        #Access the created dictionary of URLs and output a single list
        for element in extracted_page:
            for key, value in element.items():
                external_URLs.append(value)
    except:
        return ["_ERROR: problem getting external_URLs_"]

    #Make sure all URLs unique, e.g. an external URL might be repeated twice, so don't download it twice
    return set(external_URLs)

def get_URL_text(URL,headers,if_ignore_URL_error=True):
    """Get the HTML from the page, strip the tags, and output the bare text"""
    try:
        res = requests.get(URL, headers=headers, timeout=5, allow_redirects=True)
        try:
            res.raise_for_status() #Fails if error occurs, which is caught as an exception
            html_page = res.content
            
            parsed_html = BeautifulSoup(html_page,'html.parser')
            plain_text = remove_junk(parsed_html.find_all(text=True)) #Best method of getting bare text
            #plain_text = parsed_html.get_text() #Alternate method of getting bare text

            #Output text of every citation to file:
            #print("\n\n\nURL: "+URL, file=open("output.txt", "a"))
            #print(plain_text, file=open("output.txt", "a"))
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