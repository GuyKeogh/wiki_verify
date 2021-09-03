"""
__description__ = "When given the list of external links in an article and the article wikitext, output details of each citation."
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

def count_newlines_before_position(newline_indexes, start_position):
    index_count = 0
    for index in newline_indexes:
        if index > start_position:
            return index_count
        index_count+=1
    return 0

def strip_templates(wikitext):
    import re
    template_re = r'{([^"]*)}' #{ } and all text in it
    return re.sub(template_re, "", wikitext)

def extract_citation_info(external_URLs, wikitext):
    import re

    newline_indexes = [m.start() for m in re.finditer('\n', wikitext)] #Get position of every \n in the text, as these are useful reference points

    #First, find the start locations of every reference:
    reference_starts = [m.start() for m in re.finditer('<ref', wikitext)] #Both normal cites and labels start with '<ref'
    reference_ends = [m.start() for m in re.finditer('</ref>|/>', wikitext)] #Normal cites end in '</ref>', but labels end in '/>'

    citations = [] #List of tuples, with structure: (start_position, end_position, URL, how many newlines before start, label (optional))
    label_dictionary = {};

    #Check which external_URL falls between the reference start and ends:
    index = 0
    for reference in reference_starts:
        #print("----------------------------------------")
        start_position = reference_starts[index]
        end_position = reference_ends[index]
        #print(tuple((start_position,end_position)))
        citation_info = wikitext[start_position:end_position]
        external_URL = ""
        citation_group = ""

        double_quote_re = r'"([^"]*)"' #Regex pattern to get text between double quote

        #print(citation_info)

        if_URL_found = False
        for URL in external_URLs:
            if citation_info.find(URL) != -1: #Check if a known external URL is between <ref> and </ref>
                #print("Found %s in the citation template" % (URL,))

                if_URL_found = True
                external_URL = URL

                label_name_index = citation_info.find('name=')
                if label_name_index != -1: #Citation contains a group name too; the URL can then be used for citations with the same label
                    citation_group_quote = re.search(double_quote_re, citation_info[label_name_index:]).group() #Find first double quote after name=
                    citation_group = citation_group_quote[1:-1] #Remove the double quotes (first and last characters)
                    label_dictionary.update({citation_group: URL})
                break #Exit the for loop, since we have what we need from the citation

        if not if_URL_found: #No known external URL found in the template; search for a group instead
            label_name_index = citation_info.find('name=')
            if label_name_index != -1:
                citation_group = citation_group_quote[1:-1] #We now have the group name, so we can look it up in the dictionary once that's fully made
        
        newline_count = count_newlines_before_position(newline_indexes, start_position)
        citations.append(tuple((start_position, end_position, external_URL, newline_count, citation_group)))

        index+=1
    
    #Fill in the URLs for citation groups:
    index = 0
    for citation_tuple in citations:
        (start, end, cite_URL, cite_index, cite_label) = citation_tuple
        if not cite_URL and cite_label: #If there's no URL, but there is a group
            if cite_label in label_dictionary:
                cite_URL = label_dictionary[cite_label] #Get the URL using the label
            else:
                continue
        
        updated_citation_tuple = (start, end, cite_URL, cite_index, cite_label)
        citations[index] = updated_citation_tuple
        index+=1

    #print("\n###################################\n")
    #print(label_dictionary)
    #print("\n###################################\n")
    #print(citations)
    return citations