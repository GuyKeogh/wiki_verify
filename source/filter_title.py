"""
__description__ = "Filters user-inputted article titles for illegal characters"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""
import re

def from_url(url):
    url = url.split("#", 1)[0] #Get rid of hashtag and text after it
    title_language_only = url.replace(".wikipedia.org/wiki/", "]").replace("www.", "").replace("https://", "").replace("http://", "")
    #URL now in format <language>]<title> . ] used as it won't interfere with valid symbols.
    title_language_tuple = title_language_only.partition("]") #Split into two based on ] symbol
        
    return (title_language_tuple[0], title_language_tuple[2])

def handle_input_title_language(POST_name,language):
    filtered_name = filter_title(POST_name) #Removes whitespace, etc
    if_error = False
    error = ""

    #Filter bad inputs:
    title_length = len(filtered_name)
    if title_length>=256: #Article names must be less than 256 bytes
        error="An article cannot have this title (too long)."
    if title_length==0: #Nothing entered
        error="No title entered."
    if if_title_invalid_symbol_use(filtered_name): #Problematic symbol use
        error="An article cannot have this title (invalid symbol use)."
        
    if language!="en" and language !="simple":
        error = "Language not supported."
    
    return (filtered_name,if_error,error)

def filter_title(badtitle):
    """Remove excess whitespaces"""
    output = re.sub("\s\s+" , " ", badtitle.strip())
    return output

def if_title_invalid_symbol_use(title):
    """If the title has an invalid name besides spaces, return True"""
    title_length = len(title)
    if title_length==0: #To prevent out of bounds
        return True

    #Symbols not allowed at all:
    char_blacklist = [ #Characters not possible in a title
        '[',
        ']',
        '<',
        '>',
        '{',
        '}',
        '#', #Could possibly just ignore text after this
    ]
    for elem in title:
        if elem in char_blacklist:
            return True #If any symbol is bad it's all invalid.

    #Symbols not allowed as first character:
    first_char_blacklist = [
        ':',
    ]
    for symbol in first_char_blacklist:
        if symbol==title[0]:
            return True

    #Symbols not allowed as last character:
    last_char_blacklist = [
        ';',
    ]
    for symbol in last_char_blacklist:
        if symbol==title[title_length-1]:
            return True

    #Check for encoded hex:
    if bool(re.search('&#([0-9]{1,5}|x[0-9a-fA-F]{1,4});', title)):
        return True

    #3 or more consecutive tildes not allowed
    if title.find("~~~")!=-1:
        return True

    return False #No fails, so it seems technically possible
