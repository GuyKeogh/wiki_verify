 
# -*- coding: utf-8 -*-
"""
__description__ = "Backend of verification tool"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""
from source import __metadata__
from source.io import output, web_scraper
from source.dataparsing import wikitext_extract, text_tagging, article_standardise

def main(article_title, data, settings):
    #Intialise:
    processed_tags = data['processed_tags']
    segment = data['segment']
    segment_last = data['segment_last']
    external_URLs = data['external_URLs']
    text_segments = data['text_segments']
    citation_data = data['citation_data']
    section_ends = data['section_ends']
    processed_citations = data['processed_citations']
    
    HTML_out = "blank"

    if_evaluate_citations=True
    if(settings['quote?']==False and settings['NNP?']==False and settings['JJ?']==False
       and settings['NN?']==False and settings['CD?']==False):
        if_evaluate_citations=False
    #End of initialise
    
    #Start processing the article
    if segment == 0 and data['reprocess?'] == False: #First run, so needed data isn't yet stored; get that data.
        try: #Download list of external links ( FIXME: get it all from wikitext in future)
            if if_evaluate_citations:
                external_URLs = web_scraper.download_external_URLs(article_title,settings['language'])
                if len(external_URLs) == 1 and external_URLs[0] == "_ERROR: problem getting external_URLs_":
                    output.record_error(article_title, external_URLs[0])
                    data['errors']=external_URLs[0]
                    return data
        except:
            error_msg = "_ERROR: problem getting external_URLs_"
            data['errors']=error_msg
            output.record_error(article_title, error_msg)
            return data

        try: #Download article
            wikitext = web_scraper.download_wikitext(article_title,settings['language'])
            #Using wikitext and external links, get more data about the citations:
            citation_data = wikitext_extract.extract_citation_info(external_URLs, wikitext)
        except:
            data['errors']="500"
            return data
        
        #Split the article text based on its newlines (using these as segments):
        import re
        newlines = [m.start() for m in re.finditer('\n', wikitext)]
        text_segments = []
        newline_index = 0
        if_in_template = False
        for position in newlines:
            #Find the end of the section:
            position_end=0
            if(newline_index+1 < len(newlines)):
                position_end = newlines[newline_index+1]
            else:
                position_end = len(wikitext)
            
            #Find the relevant text covering that segment
            plaintext = wikitext_extract.wikitext_to_plaintext(wikitext[position:position_end]) #Text covering the segment, stripped of refs and templates
            if plaintext and not plaintext.isspace():
                if not if_in_template:
                    if '{{' in plaintext:
                        if_in_template = True
                    else:
                        #Connect the relevant citations to the segment:
                        relevant_citations = []
                        for citation in citation_data:
                            (start_pos, end_pos, external_URL, newline_count, citation_group) = citation
                            if not data['if_attach_all_citations']: # Default: citations are only evaluated when they're in same paragraph as text
                                if start_pos >= position and end_pos <= position_end:
                                    relevant_citations.append(external_URL)
                            else: # Use every citation in the article to verify every paragraph
                                relevant_citations.append(external_URL)
                        text_segments.append(tuple((position, position_end, plaintext, relevant_citations)))
                        section_ends.append(position_end)
                else: #In a template
                    if '}}' in plaintext:
                        if_in_template = False
            newline_index+=1
    else: #Session data is already saved, so just process what's needed
        #Process info for every segment that's needed:
        for wiki_part in text_segments:
            if wiki_part[0] > segment_last and wiki_part[1] <= segment:
                for cite in wiki_part[3]: # Citations covering section
                    if not cite in processed_citations: #Don't have this citation yet
                        citation_words = process_citation(cite, settings)
                        processed_citations.update({cite: citation_words})
        
                #Use relevant citations to verify section text:
                tags = text_tagging.tag_data(wiki_part[2])
                tags = text_tagging.set_needed_to_false(tags, settings)
                compiled_cite_text = []
                for cite_URL in wiki_part[3]:
                    if cite_URL in processed_citations:
                        cite_words = processed_citations[cite_URL]

                        if cite_words['text'] == '404':
                            continue
                        tags = text_tagging.compare_citation_and_text_terms(tags,
                                                        cite_words['CD'],
                                                        cite_words['JJ'],
                                                        cite_words['NN'],
                                                        cite_words['NNP'],
                                                        if_detect_NNP=settings['NNP?'],
                                                        if_detect_JJ=settings['JJ?'],
                                                        if_detect_NN=settings['NN?'],
                                                        if_detect_CD=settings['CD?'])
                        if settings['quote?']:
                            compiled_cite_text.append(cite_words['text'])
                if settings['quote?']:
                    text_quotes = text_tagging.tag_text_quotes(wiki_part[2])
                    tags = text_tagging.detect_quotes_in_multiple_texts(tags, compiled_cite_text, text_quotes)
                processed_tags = processed_tags + tags
    
    #We've done everything we need; produce output:
    HTML_out = output.parse_HTML(processed_tags)
    segment_last = segment
    data = {
        "segment": segment,
        "processed_tags": processed_tags,
        "segment_last": segment_last,
        "external_URLs": external_URLs,
        "text_segments": text_segments,
        "section_ends": section_ends,
        "citation_data": citation_data,
        "if_attach_all_citations": data['if_attach_all_citations'],
        "processed_citations": processed_citations,
        "HTML_out": HTML_out,
        "errors": ""
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
        if prohib_URL in cite_URL:
            citation_words['text'] = "404"
            return citation_words

    header = web_scraper.generate_header(settings['language'])
    text = web_scraper.get_URL_text(cite_URL, header)
    if not text:
        citation_words['text'] = "404"
        return citation_words

    return text_tagging.tag_citation_text(citation_words, text, settings)

def get_first_major_location(data):
    """Returns the best location in the article to start at when an article is entered"""
    length_sum = 0
    for segment in data['text_segments']:
        length_sum+=len(segment[2])
        if(length_sum>1000):
            return segment[1]
    return 1000

def get_next_major_location(data):
    for section in data['section_ends']:
        if data['segment'] < section:            
            if section - data['segment'] > 500:
                return section
            else:
                return data['segment']+500
    return data['section_ends'][-1]