"""
__description__ = "Downloads Wikipedia article text + its external links,
allows saving/writing files, and HTML parsing for final output"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

def load_file(file_name):
    file = open(file_name, "rt")
    read_text = file.read()
    file.close()
    return read_text

def write_file(input_text,file_name):
    file = open(file_name, "w")
    file.write(input_text)
    file.close()

def append_to_file(input_text,file_name):
    file = open(file_name, "a")
    file.write(input_text)
    file.close()

def parse_HTML(data):  
    """Create the final HTML that's output to the user"""
    
    if_header2_open = if_header3_open = if_bold_open = if_italic_open = if_paragraph_open = False
    
    combined = ""
    for word in data:
        article_word = encode_text(word[0])
        if(word[1]!="," and word[1]!= "'" and word[1]!= "." and word[0]!= "'s" #Punctuation that doesn't need space before it
           and word[1]!="``" and word[1]!="''" and word[1]!='"'): #Quotation marks
            if word[0] == "_HEADER2START_":
                combined = combined + "<h3>" #<h2> is too big, so consistently bring it down a number
                if_header2_open = True
            elif word[0] == "_HEADER2END_":
                combined = combined + "</h3>"
            elif word[0] == "_HEADER3START_":
                combined = combined + "<h4>"
                if_header3_open = True
            elif word[0] == "_HEADER3END_":
                combined = combined + "</h4>"
                if_header3_open = False
            elif word[0] == "_BOLDSTART_":
                combined = combined + "<b>"
                if_bold_open = True
            elif word[0] == "_BOLDEND_":
                combined = combined + "</b>"
                if_bold_open = False
            elif word[0] == "_ITALICSTART_":
                combined = combined + "<i>"
                if_italic_open = True
            elif word[0] == "_ITALICEND_":
                combined = combined + "</i>"
                if_italic_open = False
            elif word[0] == "_PARAGRAPHSTART_":
                combined = combined + "<p>"
                if_paragraph_open = True
            elif word[0] == "_PARAGRAPHEND_":
                combined = combined + "</p>"
                if_paragraph_open = False
            elif word[2] == 'fail':
                combined = combined + ''' <span title="'''+word[1]+'''" style="background-color: #ff0000">''' + article_word + "</span>"
            elif word[2] == 'pass':
                combined = combined + ''' <span title="'''+word[1]+'''" style="background-color: #00ff00">''' + article_word + "</span>"
            else:
                combined = combined + " " + article_word
        else: #Punctuation, so no space needed.
            combined = combined + article_word
    if if_header2_open:
        combined = combined + "</h3>"
    if if_header3_open:
        combined = combined + "</h4>"
    if if_bold_open:
        combined = combined + "</b>"
    if if_italic_open:
        combined = combined + "</i>"
    if if_paragraph_open:
        combined = combined + "</p>"
    
    return combined

def encode_text(text):
    """Encode data to help prevent XSS attacks from text in article"""
    #Most efficient way is to chain these together ( https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string )
    text = text.replace('&','&amp').replace('<','&lt').replace('>','&gt').replace('"','&quot').replace("'",'&#x27')
    return text
