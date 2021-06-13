def space_after_punctuation(data):
    #Add spaces after . and ,
    prior_elem_was_punctuation = False
    elemcount = 0
    for elem in data:
        if(prior_elem_was_punctuation == True):
            if(elem != " "):
                data = data[:elemcount] + ' ' + data[elemcount:]
                #print("Added space at ",elemcount)
                elemcount+=1 #Added element before us, putting us 1 ahead of original. Compensate.
        if(elem == "." or elem == ","):
            prior_elem_was_punctuation = True
        else:
            prior_elem_was_punctuation = False
        
        elemcount+=1
    return data

def strip_end_sections(text):
    #Strip useless parts at end (refs, see also, etc)
    References_start = text.rfind("References")
    See_also_start = text.rfind("See also")
    External_links_start = text.rfind("External links")
    Further_reading_start = text.rfind("Further reading")
    
    end_of_document = References_start
    if(See_also_start < end_of_document and See_also_start != -1):
        end_of_document = See_also_start
    if(External_links_start < end_of_document and External_links_start != -1):
        end_of_document = External_links_start
    if(Further_reading_start < end_of_document and Further_reading_start != -1):
        end_of_document = Further_reading_start
    
    if(end_of_document != -1):
        #print("End of document is at ", end_of_document)
        text = text[:end_of_document]
    
    #Save, to help debugging
    #file = open("article.txt", "w")
    #file.write(original_text)
    #file.close()
    
    return(text)
def detect_headings(text):
    #Detect locations of headings within text, and output tuples with the start and end locations of these
    title_indexes = []
    slash_n_in_row = 0
    title_index = 0 #How many characters into current title
    index = 0
    if_title = False
    for letter in text:
        if(letter == "\n"):
            slash_n_in_row += 1
            if(slash_n_in_row == 3):
                if_title = True
            else:
                if(if_title == True):
                    end = index
                    start = index - title_index
                    print("Start: ",start," end: ",end)
                    title_indexes.append(tuple((start,end)))
                if_title = False
        else:
            slash_n_in_row = 0
            if(if_title):
                title_index+=1
            else:
                title_index = 0
        index+=1
            
    print(title_indexes)
    return title_indexes

#Load article
#file = open("article.txt", "rt")
#data = file.read()

#space_after_punctuation(data)

#words = data.split() #Best to call before needed
#print('Number of words in text file :', len(words))

#print(data)

#Check for dates, and convert to ISO
#Per https://www.clarusft.com/auto-detecting-date-format-in-csv-files/ , check all dates if in ambiguous ??/??/20?? format, and if any date is > 12 it shouldn't be month
"""
#Convert
months = ['January','February','March','April','May','June','July','August','September','October','November','December']
prepositions = ['of', 'in', 'on', 'at', 'from']

words = data.split() #Update words

prior_elem_was_numeric = False
wordcount = 0
m = 0
d = 0
y = 0
startelement = 0

datetuples = []
ifDateFullySet = False
for word in words:
    strippedPunctuation = ""
    if(word in prepositions): #Ignore "1 April in 2020", etc
        wordcount+=1
        continue
    
    word_no_punctuation = word.translate(str.maketrans('', '', string.punctuation))
    if(word_no_punctuation != word):
        lastchar = word[len(word)-1]
        if(lastchar in string.punctuation):
            strippedPunctuation = lastchar
    #Convert dates in format 'Day Month Year'
    if(prior_elem_was_numeric):
        if(word_no_punctuation in months): #compare to list of months
            #print("Found month",word)
            word = months.index(word_no_punctuation)+1
            m = word
    
    #Other stuff
    #print(word)
    
    if(isinstance(word, str)): #if it's still a string
        if(word_no_punctuation.isnumeric()):
            if(d > 0):
                if(m > 0):
                    y = int(word_no_punctuation)
                    #print("found year")
                    
                    datetuple = (str(d)+" "+months[m]+", "+str(y)+strippedPunctuation,startelement,wordcount)
                    datetuples.append(datetuple)
                    #Reset
                    m = 0
                    d = 0
                    y = 0
                    prior_elem_was_numeric = False
                else:
                    m = int(word_no_punctuation)
            else:
                d = int(word_no_punctuation)
                startelement = wordcount
                
            prior_elem_was_numeric = True
            
        else:
            startelement = 0
            prior_elem_was_numeric = False
            m = 0
            d = 0
            y = 0
    
    wordcount+=1
    #print("-",wordcount)

for datetuple in datetuples[::-1]: #Access tuples backwards
    text = datetuple[0]
    startelement = datetuple[1]
    endelement = datetuple[2]
    
    number_to_delete = endelement+1-startelement
    #Remove surrounding elements
    for i in range(number_to_delete):
        del words[startelement]
                        
    words.insert(startelement,text)
                    
    #print("startelement: ",startelement)


data = " ".join(words)
"""
"""
#Close base file
file.close()

#write changes to disk
article = open("article_standardised.txt", "w")
n = article.write(data)
article.close()
"""