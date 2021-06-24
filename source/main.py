"""
__description__ = "Backend of verification tool"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""
from nltk import word_tokenize
from source import article_standardise, programIO, text_tagging, citation_scraper

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
    external_URLs_failed = []
    if if_evaluate_citations:
        external_URLs = programIO.download_external_URLs(article_title)

        unique_terms_citations_NNP = []
        unique_terms_citations_NN = []
        unique_terms_citations_JJ = []
        unique_terms_citations_CD = []
        citation_text= []
        citeindex = 0

        #Request header sent to citation server:
        citation_refferer_header = citation_scraper.generate_header(language=language,
                                                                    article_title=article_title)

        for URL in external_URLs:
            #text = programIO.load_file(str(citeindex))
            text = citation_scraper.get_URL_text(URL,citation_refferer_header,if_ignore_URL_error)
            if text != "404":
                try: #Do the processing, which is a good enough delay before making another request.
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
                    #programIO.write_file(text,str(citeindex)) #Save citation text to file
                    citation_text.append(text)
                except Exception as exc:
                    external_URLs_failed.append(URL)
                    if not if_ignore_URL_error:
                        print("Error with URL '",URL,"' with error ",exc)
            elif not if_ignore_URL_error:
                text = input("Copy and paste text of above URL, or leave blank: ")
                tokenized_citation = text_tagging.eval_citation(text)
                citetext_NNP = text_tagging.eval_citation_for_type(tokenized_citation, 'NNP')
                unique_terms_citations_NNP = unique_terms_citations_NNP + citetext_NNP
            else:
                external_URLs_failed.append(URL)
            citeindex+=1

        #Compare unique citation terms of specific type and article text of the same type
        text_JJ = []
        text_NN = []
        text_NNP = []
        text_CD = []
        if if_detect_JJ:
            text_JJ = text_tagging.tag_text_of_type("JJ",data)
            data = text_tagging.tag_comparisons(text_JJ, unique_terms_citations_JJ, data)
        if if_detect_NNP:
            text_NNP = text_tagging.tag_text_of_type("NNP",data)
            data = text_tagging.tag_comparisons(text_NNP, unique_terms_citations_NNP, data)
        if if_detect_NN:
            text_NN = text_tagging.tag_text_of_type("NN",data)
            data = text_tagging.tag_comparisons(text_NN, unique_terms_citations_NN, data)
        if if_detect_CD:
            text_CD = text_tagging.tag_text_of_type("CD",data)
            data = text_tagging.tag_comparisons(text_CD, unique_terms_citations_CD, data)

        #Compare quotes
        if if_detect_quote:
            for quote in text_quotes:
                if_quote_in_citation = False
                for citation in citation_text:
                    if if_quote_in_citation == False: #Just needs to be in one citation
                        if_quote_in_citation = text_tagging.check_quote_in_text(quote, citation)

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
                        if len(quote_list)==index-quote_in_data_startword: #Detected a quote
                            for k in range(quote_in_data_startword, index, 1):
                                if not if_quote_in_citation:
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

    #Write html output as string:
    html_output = programIO.parse_HTML(data)
    output = (html_output,external_URLs_failed,data,text_quotes)
    return output
