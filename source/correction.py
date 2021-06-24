"""
__description__ = "Handles user-inputted URL text from failed URLs to verify information for final"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from nltk import word_tokenize
from source import programIO, text_tagging

def correction(article_title,data,text,text_quotes,language="en",
         if_ignore_URL_error = True,
         if_detect_quote = True,
         if_detect_NNP = True,
         if_detect_JJ = False,
         if_detect_NN = False,
         if_detect_CD = True):
    citation_text = text_tagging.tag_data(text)

    unique_terms_citations_NNP = []
    unique_terms_citations_NN = []
    unique_terms_citations_JJ = []
    unique_terms_citations_CD = []
    citation_text= []

    if(text!=""):
        tokenized_citation = text_tagging.eval_citation(text)
        #NN (Proper noun, singular)
        if if_detect_NN:
            citetext_NN = text_tagging.eval_citation_for_type(tokenized_citation, 'NN')
            unique_terms_citations_NN = unique_terms_citations_NN + citetext_NN
        #NNP (Proper noun, plural)
        if if_detect_NNP:
            citetext_NNP = text_tagging.eval_citation_for_type(tokenized_citation, 'NNP')
            unique_terms_citations_NNP = unique_terms_citations_NNP + citetext_NNP
        #JJ (Adjective)
        if if_detect_JJ:
            citetext_JJ = text_tagging.eval_citation_for_type(tokenized_citation, 'JJ')
            unique_terms_citations_JJ = unique_terms_citations_JJ + citetext_JJ
        #CD (Cardinal number)
        if if_detect_CD:
            citetext_CD = text_tagging.eval_citation_for_type(tokenized_citation, 'CD')
            unique_terms_citations_CD = unique_terms_citations_CD + citetext_CD
        citation_text.append(text)

        #Compare unique citation terms of specific type and article text of the same type
        text_JJ = []
        text_NN = []
        text_NNP = []
        text_CD = []
        if if_detect_JJ:
            text_JJ = text_tagging.tag_text_of_type("JJ", data)
            data = text_tagging.tag_comparisons(text_JJ, unique_terms_citations_JJ, data)
        if if_detect_NNP:
            text_NNP = text_tagging.tag_text_of_type("NNP", data)
            data = text_tagging.tag_comparisons(text_NNP, unique_terms_citations_NNP, data)
        if if_detect_NN:
            text_NN = text_tagging.tag_text_of_type("NN", data)
            data = text_tagging.tag_comparisons(text_NN, unique_terms_citations_NN, data)
        if if_detect_CD:
            text_CD = text_tagging.tag_text_of_type("CD", data)
            data = text_tagging.tag_comparisons(text_CD, unique_terms_citations_CD, data)

        #Compare quotes
        if(if_detect_quote):
            for quote in text_quotes:
                ifTrue = text_tagging.check_quote_in_text(quote, text)
                
                quote_in_data_startword = 0
                index = 0
                if_in_quote = False
                quote_list = word_tokenize(quote) #List of each word in quote
                #Find quote in data
                for word in data:
                    if not if_in_quote:
                        if word[0]==quote_list[0]:
                            if_in_quote = True
                            quote_in_data_startword = index
                    else: #If we seem to be in a quote, check it's still true
                        if len(quote_list)==(index-quote_in_data_startword): #Detected a quote
                            for k in range(quote_in_data_startword, index, 1):
                                if ifTrue == False:
                                    data[k][1] = 'quote'
                                    data[k][2] = 'fail'
                                else:
                                    data[k][1] = 'quote'
                                    data[k][2] = 'pass'

                            if_in_quote = False
                            quote_in_data_startword = 0
                        elif word[0]!=quote_list[index-quote_in_data_startword]:
                            if_in_quote = False
                            quote_in_data_startword = 0
                    index+=1

    html_output = programIO.parse_HTML(data)
    return html_output
