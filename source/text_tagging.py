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