"""
__description__ = "Downloads Wikipedia article text + its external links,
allows saving/writing files, and HTML parsing for final output"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

import requests
def download_article(article_title):
    response = requests.get(
    'https://en.wikipedia.org/w/api.php',
    params={
    'action': 'query',
    'titles': article_title,
    'format': 'json',
    'prop': 'extracts',
    'explaintext': True,
    'exsectionformat': 'plain',
    }
    ).json()
    page = next(iter(response['query']['pages'].values()))
    extracted_page = page['extract']
    
    return extracted_page
def download_external_URLs(article_title):
    response = requests.get(
    'https://en.wikipedia.org/w/api.php',
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

def load_file(file_name):
    file = open(file_name, "rt")
    read_text = file.read()
    file.close()
    return read_text

def write_file(input_text,file_name):
    file = open(file_name, "w")
    file.write(input_text)
    file.close()

def parse_HTML(data):    
    combined = ""
    for word in data:
        article_word = encode_text(word[0])
        if(word[0] == "_BREAK2_"):
            combined = combined + "<br><br><strong>"
        elif(word[0] == "_BREAK1_"):
            combined = combined + "</strong><br>"
        elif(word[2] == 'fail'):
            combined = combined + ''' <span title="'''+word[1]+'''" style="background-color: #ff0000">''' + article_word + "</span>"
        elif(word[2] == 'pass'):
            combined = combined + ''' <span title="'''+word[1]+'''" style="background-color: #00ff00">''' + article_word + "</span>"
        else:
            combined = combined + " " + article_word
    return combined

def encode_text(text):
    #Encode data to help prevent XSS attacks from text in article:
    #Most efficient way is to chain these together ( https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string )
    text = text.replace('&','&amp').replace('<','&lt').replace('>','&gt').replace('"','&quot').replace("'",'&#x27')
    return text