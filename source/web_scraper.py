"""
__description__ = "Extracts plaintext from external link URL"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

import re
import requests
from bs4 import BeautifulSoup
from source import __metadata__

def download_article(article_title, language):
    """Download the Wikipedia article text and mark safe HTML elements with codes so they remain the same"""
    response = requests.get(
    'https://'+language+'.wikipedia.org/w/api.php',
    params={
    'action': 'query',
    'titles': article_title,
    'format': 'json',
    'prop': 'extracts',
    'exsectionformat': 'plain',
    }
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
    response = requests.get(
    'https://'+language+'.wikipedia.org/w/api.php',
    params={
    'action': 'query',
    'titles': article_title,
    'format': 'json',
    'prop': 'extlinks',
    }
    ).json()
    page = next(iter(response['query']['pages'].values()))
    extracted_page = page['extlinks']
    
    #Access the created dictionary of URLs and output a single list
    external_URLs = []
    for element in extracted_page:
        for key, value in element.items():
            external_URLs.append(value)

    #Make sure all URLs unique, e.g. an external URL might be repeated twice, so don't download it twice
    return set(external_URLs)

def generate_header(language="", article_title=""):
    """Creates the HTTP header which is sent when requesting citations"""
    header = {
        'User-Agent': 'wiki_verify/'+__metadata__.__VERSION__,
        'Accept-Language': "en-US,en;q=0.5",
        'referer': "https://"+language+".wikipedia.org/"+article_title.replace(" ", "_"),
        'UPGRADE-INSECURE-REQUESTS': "1",
        'Save-Data': "on",
        }
    return header

def get_URL_text(URL,headers,if_ignore_URL_error=True):
    """Get the HTML from the page, strip the tags, and output the bare text"""
    try:
        res = requests.get(URL, headers=headers, timeout=5, allow_redirects=True)
        try:
            res.raise_for_status() #Fails if error occurs, which is caught as an exception
            html_page = res.content
            parsed_html = BeautifulSoup(html_page,'html.parser')
            plain_text = remove_junk(parsed_html.find_all(text=True))
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
