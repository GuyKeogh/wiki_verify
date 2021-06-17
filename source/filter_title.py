"""
__description__ = "Filters user-inputted article titles for illegal characters"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""
import re

def filter_title(badtitle):
    #Remove excess whitespaces
    output = re.sub("\s\s+" , " ", badtitle.strip())
    
    #NB: act on Question marks and plus signs
    
    return output

def if_title_invalid_symbol_use(title): #If the title has an invalid name besides spaces, return True
    title_length = len(title)
    if(title_length==0): #To prevent out of bounds
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
    for t in title:
        if t in char_blacklist:
            return True #If any symbol is bad it's all invalid.
    
    #Symbols not allowed as first character:
    first_char_blacklist = [
        ':',
    ]
    for symbol in first_char_blacklist:
        if(symbol==title[0]):
            return True
    
    
    #Symbols not allowed as last character:
    last_char_blacklist = [
        ';',
    ]
    for symbol in last_char_blacklist:
        if(symbol==title[title_length-1]):
            return True
    
    #Check for encoded hex:
    if(bool(re.search('&#([0-9]{1,5}|x[0-9a-fA-F]{1,4});', title))==True):
        return True
    
    #3 or more consecutive tildes not allowed
    if(title.find("~~~")!=-1):
        return True        
    
    return False #No fails, so it seems technically possible