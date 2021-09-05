"""
__description__ = "Handles user-inputted URL text from failed URLs to verify information for final"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from source import text_tagging

def add_input(input_text, data, settings):
    each_URL_location = []
    processed_citations = data['processed_citations']

    for external_URL in processed_citations:
        print(external_URL)
        URL = external_URL.replace("https://","").replace("http://","").replace("www.","")
        position = input_text.find(URL)
        URL_indexes = dict()
        if position != -1:
            URL_indexes.update({position+len(URL): URL})
            print("Found URL. New index: " + str(URL_indexes))
        
        if not URL_indexes: #No URLs supplied
            data['reprocess?'] = False
            break
        else:
            indexes = []
            for index in URL_indexes:
                indexes.append(index) # Get the index from the dictionary with structure {index: URL}

            indexes = sorted(indexes)
            indexes_index = 0
            for index in indexes:
                citation_words = {
                    "text": "",
                    "CD": [],
                    "JJ": [],
                    "NN": [],
                    "NNP": []
                }

                position_end=0
                if(indexes_index+1 < len(indexes)):
                    position_end = indexes[indexes_index+1] # Start of next URL in list
                else:
                    position_end = len(input_text) #End of inputted text - no more URLs
                text = input_text[position:position_end]

                citation_words = text_tagging.tag_citation_text(citation_words, text, settings)
                processed_citations[external_URL] = citation_words
                indexes_index+=1
    
    data['processed_citations'] = processed_citations
    return data