"""
__description__ = "Raw text processing, by tagging word types with NLTK, and detecting quotes"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

import nltk
import re #Regex
def tag_data(text):
    #Extract info
    sentences = nltk.sent_tokenize(text) #Organize into individual sentences
    data = []
    for sent in sentences:
        data = data + nltk.pos_tag(nltk.word_tokenize(sent))
    
    tagged_data = []
    index = 0
    for word in data:
        tagged_data.append([word[0],word[1], 'none'])
        index+=1
    return tagged_data
def tag_text_of_type(tag_type,data):
    #Only output words of specific type
    text_of_tag = []
    index = 0
    for word in data:
        if tag_type in word[1]: 
            text_of_tag.append(tuple((word[0], index)))
        index+=1
    return text_of_tag
def tag_text_quotes(text):
    #Detects all info in single or double quotes, and outputs all these as strings in a list
    matches=re.findall(r'\"(.+?)\"',text)
    return matches
def eval_citation(citation_text):
    sentences = nltk.sent_tokenize(citation_text) #Organize into individual sentences
    data = []
    for sent in sentences:
        data = data + nltk.pos_tag(nltk.word_tokenize(sent))
    return set(data)

def eval_citation_for_type(citation_text, key):
    #Only output words of specific type stated in key
    unique_terms_cite = []
    for word in citation_text:
        if key in word[1]: 
            unique_terms_cite.append(word[0])
    return unique_terms_cite

def check_quote_in_text(quote_string,citation_text):
    if(citation_text.find(quote_string) != -1):
        return True
    else:
        return False
def tag_comparisons(term,text_of_tag,unique_terms_citations_of_tag,data):
    for elem in text_of_tag:
        if(data[elem[1]][2] != 'pass'):
            if elem[0] not in unique_terms_citations_of_tag:
                data[elem[1]][2] = 'fail'
            else:
                data[elem[1]][2] = 'pass'
    return data
