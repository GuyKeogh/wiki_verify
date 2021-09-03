 
# -*- coding: utf-8 -*-
"""
__description__ = "Backend of verification tool"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""
import article_standardise, programIO, text_tagging, web_scraper, __metadata__
from dataparsing import wikitext_extract

def main(article_title, data, settings = ("en", True, False, False, True, True)):
    #Intialise:

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
            return ("500",[],[],[])
        
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
            
            #Find the relevant text covering that segment:
            text_segments.append(tuple((position, position_end, wikitext[position:position_end], relevant_citations)))
            newline_index+=1

        HTML_out = "Working..."
    else: #Session data is already saved, so just process what's needed
        segments_needed = range(segment_last, segment)
        #Process info for every segment that's needed:
        for part in text_segments:
            if part[0] > segment_last and part[1] <= segment:
                print(str(part[0]) + " has citations: " + str(part[3]))
    
    #We've done everything we need; produce output:
    segment_last = segment
    output = {
        "segment": segment,
        "segment_last": segment_last,
        "external_URLs": external_URLs,
        "text_segments": text_segments,
        "citation_data": citation_data,
        "processed_citations": processed_citations,
        "HTML_out": HTML_out
    }
    return output

settings = ("en", True, False, False, True, True)
article_title = input("Enter article name")

data = {
        "segment": 0,
        "segment_last": 0,
        "external_URLs": [],
        "text_segments": [],
        "citation_data": [],
        "processed_citations": [],
}
output = main(article_title, data, settings)

#print(output["HTML_out"])
#print(output["text_segments"])

#print("###############################################")

output["segment"] = 4000

output_2 = main(article_title, output, settings)
print(output_2["HTML_out"])