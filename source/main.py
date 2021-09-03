 
# -*- coding: utf-8 -*-
"""
__description__ = "Backend of verification tool"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""
from source import article_standardise, programIO, text_tagging, web_scraper, __metadata__
from source.dataparsing import wikitext_extract

def main(article_title, data, settings = ("en", True, False, False, True, True)):
    #Intialise:
    tags = []
    processed_tags = []
    segment = data['segment']
    segment_last = data['segment_last']
    external_URLs = data['external_URLs']
    text_segments = data['text_segments']
    citation_data = data['citation_data']
    processed_citations = data['processed_citations']
    (language, if_detect_CD, if_detect_JJ, if_detect_NN, if_detect_NNP, if_detect_quote) = settings
    
    external_URLs_failed = []
    HTML_out = "blank"

    if_evaluate_citations=True
    if(if_detect_quote==False and if_detect_NNP==False and if_detect_JJ==False
       and if_detect_NN==False and if_detect_CD==False):
        if_evaluate_citations=False
    #End of initialise
    
    #Start processing the article
    if segment == 0: #First run, so needed data isn't yet stored; get that data.
        try: #Download list of external links (future update: get it all from wikitext)
            if if_evaluate_citations:
                external_URLs = web_scraper.download_external_URLs(article_title,language)
                if len(external_URLs) == 1 and external_URLs[0] == "_ERROR: problem getting external_URLs_":
                    programIO.record_error(article_title, external_URLs[0])
                    return (external_URLs[0],[],[],[])
        except:
            error_msg = "_ERROR: problem getting external_URLs_"
            programIO.record_error(article_title, error_msg)
            return (error_msg,[],[],[])

        try: #Download article
            wikitext = web_scraper.download_wikitext(article_title,language)
            #Using wikitext and external links, get more data about the citations:
            citation_data = wikitext_extract.extract_citation_info(external_URLs, wikitext)
        except:
            data["HTML_out"] = "500"
            return data
        
        #Split the article text based on its newlines (using these as segments):
        import re
        newlines = [m.start() for m in re.finditer('\n', wikitext)]
        text_segments = []
        newline_index = 0
        for position in newlines:
            #Find the end of the section:
            position_end=0
            if(newline_index+1 < len(newlines)):
                position_end = newlines[newline_index+1]
            else:
                position_end = len(wikitext)
            
            #Connect the relevant citations to the segment:
            relevant_citations = []
            for citation in citation_data:
                (start_pos, end_pos, external_URL, newline_count, citation_group) = citation
                if start_pos >= position and end_pos <= position_end:
                    relevant_citations.append(external_URL)
            
            #Find the relevant text covering that segment
            plaintext = wikitext_extract.strip_templates(wikitext[position:position_end]) #Text covering the segment, stripped of refs and templates
            text_segments.append(tuple((position, position_end, plaintext, relevant_citations)))
            newline_index+=1

        HTML_out = "Working..."
    else: #Session data is already saved, so just process what's needed
        #Process info for every segment that's needed:
        for wiki_part in text_segments:
            if wiki_part[0] > segment_last and wiki_part[1] <= segment:
                for cite in wiki_part[3]:
                    if not cite in processed_citations:
                        citation_words = process_citation(cite, settings)
                        processed_citations.update({cite: citation_words})
        
                #Use relevant citations to verify section text:
                tags = text_tagging.tag_data(wiki_part[2])
                text_quotes = text_tagging.tag_text_quotes(wiki_part[2])
                compiled_cite_text = ""
                for cite_URL in wiki_part[3]:
                    if cite_URL in processed_citations:
                        cite_words = processed_citations[cite_URL]

                        if cite_words['text'] == '404':
                            continue
                        tags = text_tagging.compare_citation_and_text_terms(data,
                                                        cite_words['CD'],
                                                        cite_words['JJ'],
                                                        cite_words['NN'],
                                                        cite_words['NNP'],
                                                        if_detect_NNP=if_detect_NNP,
                                                        if_detect_JJ=if_detect_JJ,
                                                        if_detect_NN=if_detect_NN,
                                                        if_detect_CD=if_detect_CD)
                        if if_detect_quote:
                            compiled_cite_text = compiled_cite_text + cite_words['text']
                if if_detect_quote:
                    tags = text_tagging.detect_quotes_in_multiple_texts(tags, compiled_cite_text, text_quotes)
                processed_tags = processed_tags + tags
                tags = []
    
    #We've done everything we need; produce output:
    HTML_out = programIO.parse_HTML(processed_tags)
    segment_last = segment
    data = {
        "segment": segment,
        "segment_last": segment_last,
        "external_URLs": external_URLs,
        "text_segments": text_segments,
        "citation_data": citation_data,
        "processed_citations": processed_citations,
        "HTML_out": HTML_out
    }
    return data

def process_citation(cite_URL, settings):
    citation_words = {
        "text": "", #Need to keep this to handle quotes
        "CD": [],
        "JJ": [],
        "NN": [],
        "NNP": []
    }

    for prohib_URL in __metadata__.__DO_NOT_SCRAPE_URLS__:
        if cite_URL.find(prohib_URL)!=-1:
            citation_words['text'] = "404"
            return citation_words
    
    header = web_scraper.generate_header(settings[0])
    text = web_scraper.get_URL_text(cite_URL, header)

    if text != "404":
        (terms_citations_CD,
            terms_citations_JJ,
            terms_citations_NN,
            terms_citations_NNP) = text_tagging.get_citation_unique_terms(text, settings)
        
        citation_words['NN'] = terms_citations_NN
        citation_words['NNP'] = terms_citations_NNP
        citation_words['JJ'] = terms_citations_JJ
        citation_words['CD'] = terms_citations_CD
        citation_words['text'] = text

    return citation_words