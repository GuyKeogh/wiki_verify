"""
__description__ = "Extracts plaintext from external link URL"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from bs4 import BeautifulSoup    
import requests
import re

def get_URL_text(URL,headers,if_ignore_URL_error=True):
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
            if(if_ignore_URL_error==False):
                print('There was a problem: %s' % (exc))
            return "404"
    except Exception as exc:
        if(if_ignore_URL_error==False):
            print('There was a problem requesting the URL: %s' % (exc))

def remove_junk(text):
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