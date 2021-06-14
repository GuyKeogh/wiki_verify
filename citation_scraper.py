#https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/
def get_URL_text(URL):
    from bs4 import BeautifulSoup    
    import requests
    try:
        res = requests.get(URL)
        
        try:
            res.raise_for_status() #if there are errors it excepts
            
            html_page = res.content
            parsed_html = BeautifulSoup(html_page, 'html.parser')
            text = parsed_html.find_all(text=True)
            
            
            plain_text = remove_junk(text)
            return plain_text
        except Exception as exc:
            print('There was a problem: %s' % (exc))
            return "404"
        
    except Exception as exc:
        print('There was a problem requesting the URL: %s' % (exc))
    

def remove_junk(text):
    import re
    output = ''
    #Rm tags and scripts
    blacklist = [ #Add whatever isn't needed in HTML
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
    
    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)
    
    #Strip tabs, newlines, etc
    output = re.sub(r'(^[ \t]+|[ \t]+(?=:))', '', output, flags=re.M)
    output = " ".join(output.split())
    
    return output.strip()