"""
__description__ = "Backend of verification tool"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""
import nltk
from nltk import word_tokenize
from source import article_standardise
from source import programIO
from source import text_tagging
from source import citation_get

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

def main(article_title,language="en",
         if_ignore_URL_error = True,
         if_detect_quote = True, if_detect_NNP = True, if_detect_JJ = False, if_detect_NN = False, if_detect_CD = True
         ):
    
    try: #Download article
        original_text = programIO.download_article(article_title)
    except:
        return "500"
    
    article_text = article_standardise.strip_end_sections(original_text)
    
    text_quotes = text_tagging.tag_text_quotes(article_text)
    article_text = article_standardise.space_after_punctuation(article_text)
    headings = article_standardise.detect_headings(article_text)
    
    for heading in reversed(headings):
        article_text = article_text[:heading[1]] + ' _BREAK1_ ' + article_text[heading[1]:]
        article_text = article_text[:heading[0]] + ' _BREAK2_ ' + article_text[heading[0]:]
    
    data = text_tagging.tag_data(article_text)
    
    if_evaluate_citations=True
    if(if_detect_quote==False and if_detect_NNP==False and if_detect_JJ==False
       and if_detect_NN==False and if_detect_CD==False):
        if_evaluate_citations=False #If we're not doing anything with the citations, don't download or process them
    
    #Handle citations:
    if(if_evaluate_citations):
        external_URLs = programIO.download_external_URLs(article_title)
        
        unique_terms_citations_NNP = []
        unique_terms_citations_NN = []
        unique_terms_citations_JJ = []
        unique_terms_citations_CD = []
        citation_text= []
        citeindex = 0
        for URL in external_URLs:
            #text = programIO.load_file(str(citeindex))
            text = citation_get.get_citation(URL)
            if(text != "404"):
                try:
                    #programIO.write_file(text,str(citeindex)) #Save citation text to file
                    
                    tokenized_citation = eval_citation(text)
                    #NN (Proper noun, singular)
                    if(if_detect_NN):
                        citetext_NN = eval_citation_for_type(tokenized_citation, 'NN')
                        unique_terms_citations_NN = unique_terms_citations_NNP + citetext_NN
                    #NNP (Proper noun, plural)
                    if(if_detect_NNP):
                        citetext_NNP = eval_citation_for_type(tokenized_citation, 'NNP')
                        unique_terms_citations_NNP = unique_terms_citations_NNP + citetext_NNP
                    #JJ (Adjective)
                    if(if_detect_JJ):
                        citetext_JJ = eval_citation_for_type(tokenized_citation, 'JJ')
                        unique_terms_citations_JJ = unique_terms_citations_JJ + citetext_JJ
                    #CD (Cardinal number)
                    if(if_detect_CD):
                        citetext_CD = eval_citation_for_type(tokenized_citation, 'CD')
                        unique_terms_citations_CD = unique_terms_citations_CD + citetext_CD
    
                    citation_text.append(text)
                except Exception as exc:
                    print("Error with URL '",URL,"' with error ",exc)
            elif(if_ignore_URL_error == False):
                text = input("Copy and paste text of above URL, or leave blank: ")
                tokenized_citation = eval_citation(text)
                citetext_NNP = eval_citation_for_type(tokenized_citation, 'NNP')
                unique_terms_citations_NNP = unique_terms_citations_NNP + citetext_NNP
            citeindex+=1
        
        #Compare unique citation terms of specific type and article text of the same type
        text_JJ = []
        text_NN = []
        text_NNP = []
        text_CD = []
        if(if_detect_JJ):
            text_JJ = text_tagging.tag_text_of_type("JJ",data)
            data = tag_comparisons("JJ",text_JJ,unique_terms_citations_JJ,data)
        if(if_detect_NNP):
            text_NNP = text_tagging.tag_text_of_type("NNP",data)
            data = tag_comparisons("NNP",text_NNP,unique_terms_citations_NNP,data)
        if(if_detect_NN):
            text_NN = text_tagging.tag_text_of_type("NN",data)
            data = tag_comparisons("NN",text_NN,unique_terms_citations_NN,data)
        if(if_detect_CD):
            text_CD = text_tagging.tag_text_of_type("CD",data)
            data = tag_comparisons("CD",text_CD,unique_terms_citations_CD,data)
    
        #Compare quotes
        if(if_detect_quote):
            for quote in text_quotes:
                ifTrue = False
                for citation in citation_text:
                    if(ifTrue == False): #Just needs to be in one citation
                        ifTrue = check_quote_in_text(quote,citation)
                
                quote_in_data_startword = 0
                index = 0
                if_in_quote = False
                quote_list = word_tokenize(quote) #List of each word in quote
                
                #Find quote in data
                for word in data:
                    if(if_in_quote==False):
                        if(word[0]==quote_list[0]):
                            if_in_quote = True
                            quote_in_data_startword = index
                    else: #If we seem to be in a quote, check it's still true
                        if(len(quote_list)==index-quote_in_data_startword): #Successfully detected a quote
                            for k in range(quote_in_data_startword,index,1):
                                if ifTrue == False:
                                    data[k][1] = 'quote'
                                    data[k][2] = 'fail'
                                else:
                                    data[k][1] = 'quote'
                                    data[k][2] = 'pass'
                            
                            if_in_quote = False
                            quote_in_data_startword = 0
                        elif(word[0]!=quote_list[index-quote_in_data_startword]):
                            if_in_quote = False
                            quote_in_data_startword = 0
                    index+=1

    #Write html output as string:
    html_output = programIO.parse_HTML(data)
    return html_output