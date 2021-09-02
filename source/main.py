 
# -*- coding: utf-8 -*-
"""
__description__ = "Backend of verification tool"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""
from source import article_standardise, programIO, text_tagging, web_scraper, __metadata__
from dataparsing import wikitext_extract

def main(article_title, data, settings = ("en", True, False, False, True, True)):

    (segment, original_text, citation_info, citation_text) = data
    (language, if_detect_CD, if_detect_JJ, if_detect_NN, if_detect_NNP, if_detect_quote) = settings
    
    if_evaluate_citations=True
    if(if_detect_quote==False and if_detect_NNP==False and if_detect_JJ==False
       and if_detect_NN==False and if_detect_CD==False):
        if_evaluate_citations=False

    if segment == 0:
        try: #Download article
            original_text = wikitext_extract.strip_templates(web_scraper.download_wikitext(article_title,language))
        except:
            return ("500",[],[],[])

    return output