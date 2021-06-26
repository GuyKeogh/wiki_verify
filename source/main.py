# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 19:59:07 2021

@author: guyke
"""

"""
__description__ = "Backend of verification tool"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""
from source import article_standardise, programIO, text_tagging, web_scraper, __metadata__, analytics

def main(article_title,language="en",
         if_ignore_URL_error = True,
         if_detect_quote = True, if_detect_NNP = True, if_detect_JJ = False, if_detect_NN = False, if_detect_CD = True
         ):

    try: #Download article
        original_text = web_scraper.download_article(article_title,language)
    except:
        return ("500",[],[],[])

    article_text = article_standardise.strip_end_sections(original_text)

    text_quotes = text_tagging.tag_text_quotes(article_text)
    article_text = article_standardise.space_after_punctuation(article_text)

    data = text_tagging.tag_data(article_text)

    if_evaluate_citations=True
    if(if_detect_quote==False and if_detect_NNP==False and if_detect_JJ==False
       and if_detect_NN==False and if_detect_CD==False):
        if_evaluate_citations=False #If we're not doing anything with the citations, don't download or process them
    
    #Handle citations:
    external_URLs_failed = []
    if if_evaluate_citations:
        external_URLs = web_scraper.download_external_URLs(article_title,language)
        print(external_URLs, file=open("URLs.txt", "a"))
        
        if __metadata__.__IF_WEB__ == True and len(external_URLs)>__metadata__.__WEB_EXTERNAL_URL_LIMIT__:
            return ("_ERROR: too many external_URLs_",[],[],[])
        else:
            analytics.total_urls_requested += len(external_URLs)
        
        unique_terms_citations_NNP = []
        unique_terms_citations_NN = []
        unique_terms_citations_JJ = []
        unique_terms_citations_CD = []
        citation_text= []
        citeindex = 0

        #Request header sent to citation server:
        citation_refferer_header = web_scraper.generate_header(language=language,
                                                                    article_title=article_title)

        for URL in external_URLs:
            if_get_URL_text = True
            text = ""
            for prohib_URL in __metadata__.__DO_NOT_SCRAPE_URLS__:
                if(URL.find(prohib_URL)!=-1):
                    if_get_URL_text = False
                    text = "404"
                    break #Don't try other URLs in list
            
            if if_get_URL_text==True:
                text = web_scraper.get_URL_text(URL,
                                                citation_refferer_header,
                                                if_ignore_URL_error)
            if text != "404":
                try: #Do the processing, which is a good enough delay before making another request.
                    (terms_citations_CD_to_append,
                     terms_citations_JJ_to_append,
                     terms_citations_NN_to_append,
                     terms_citations_NNP_to_append) = text_tagging.get_citation_unique_terms(text,
                                                                 if_detect_NNP=if_detect_NNP,
                                                                 if_detect_JJ=if_detect_JJ,
                                                                 if_detect_NN=if_detect_NN,
                                                                 if_detect_CD=if_detect_CD)
                    #Add previous results to the total:
                    unique_terms_citations_NN = unique_terms_citations_NN + terms_citations_NN_to_append
                    unique_terms_citations_NNP = unique_terms_citations_NNP + terms_citations_NNP_to_append
                    unique_terms_citations_JJ = unique_terms_citations_JJ + terms_citations_JJ_to_append
                    unique_terms_citations_CD = unique_terms_citations_CD + terms_citations_CD_to_append
                    
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

        data = text_tagging.compare_citation_and_text_terms(data,
                                               unique_terms_citations_CD,
                                               unique_terms_citations_JJ,
                                               unique_terms_citations_NN,
                                               unique_terms_citations_NNP,
                                               if_detect_NNP=if_detect_NNP,
                                               if_detect_JJ=if_detect_JJ,
                                               if_detect_NN=if_detect_NN,
                                               if_detect_CD=if_detect_CD)

        #Compare quotes
        if if_detect_quote:
            data = text_tagging.detect_quotes_in_multiple_texts(data, citation_text, text_quotes)

    #Write html output as string:
    html_output = programIO.parse_HTML(data)
    analytics.total_urls_failed += len(external_URLs_failed)
    output = (html_output, external_URLs_failed, data, text_quotes)
    return output