"""
__description__ = "Handles user-inputted URL text from failed URLs to verify information for final"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from source import programIO, text_tagging

def correction(article_title,
               data,
               input_text,text_quotes,
               language="en",
               if_detect_quote=False,
               if_detect_NNP=False,
               if_detect_JJ=False,
               if_detect_NN=False,
               if_detect_CD=False):
    """Takes the user-inputted citation text, processes it, and gives the final program output"""

    if input_text!="":
        (unique_terms_citations_CD,
         unique_terms_citations_JJ,
         unique_terms_citations_NN,
         unique_terms_citations_NNP) = text_tagging.get_citation_unique_terms(input_text,
                                                                 if_detect_NNP=if_detect_NNP,
                                                                 if_detect_JJ=if_detect_JJ,
                                                                 if_detect_NN=if_detect_NN,
                                                                 if_detect_CD=if_detect_CD)

        data = text_tagging.compare_citation_and_text_terms(data,
                                               unique_terms_citations_CD,
                                               unique_terms_citations_JJ,
                                               unique_terms_citations_NN,
                                               unique_terms_citations_NNP,
                                               if_detect_NNP=if_detect_NNP,
                                               if_detect_JJ=if_detect_JJ,
                                               if_detect_NN=if_detect_NN,
                                               if_detect_CD=if_detect_CD)
        if(if_detect_quote):
            data = text_tagging.detect_quotes_in_string(data, input_text, text_quotes)

    html_output = programIO.parse_HTML(data)
    return html_output
