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

def wikitext_to_plaintext(wikitext):
    import re
    plaintext = "_PARAGRAPHSTART_ "+wikitext #Each segments is its own paragraph, so add tag

    plaintext = plaintext.replace("\n", "") #Remove newlines (\n)
    plaintext = plaintext.replace("``", '"')
    
    #Remove text between normal ref tags:
    ref_starts = [m.start() for m in re.finditer('<ref>', plaintext)]
    ref_ends = [m.start() for m in re.finditer('</ref>', plaintext)]
    ref_starts = ref_starts[::-1] #Reverse list
    ref_ends = ref_ends[::-1]
    if ref_starts and len(ref_starts) == len(ref_ends):
        index = 0
        for start in ref_starts:
            plaintext = plaintext[:ref_starts[index]] + "" + plaintext[ref_ends[index]+6:]
            index+=1
    plaintext = re.sub(r'\<.*?\>', '', plaintext) #Remove <ref name=":0">, etc

    plaintext = re.sub(r'{{([^"]*)}}', "", plaintext) #Remove templates: {{ }} and all text in them
    plaintext = re.sub(r'{([^"]*)}', "", plaintext) #Remove templates: { } and all text in them

    #Handle wikilinks (e.g. [[Wikipedia]] and [[text you see|Wikipedia]] )
    link_starts = [m.start() for m in re.finditer('\\[\\[', plaintext)]
    link_ends = [m.start() for m in re.finditer(']]', plaintext)]
    link_starts = link_starts[::-1] #Reverse list
    link_ends = link_ends[::-1]
    if link_starts and len(link_starts) == len(link_ends):
        index = 0
        for start in link_starts:
            wikilink_text = plaintext[link_starts[index]+2:link_ends[index]] #+2 to ignore the [[
            if "Category:" in wikilink_text or "File:" in wikilink_text:
                wikilink_text = ""
            elif "|" in wikilink_text:
                wikilink_text = wikilink_text.partition("|")[0]
            
            #Text until the start of the wikilink + the new text + text after the wikilink:
            plaintext = plaintext[:link_starts[index]] + wikilink_text + plaintext[link_ends[index]+2:]
            index+=1

    #Replace headers with tags:
    if plaintext.startswith("_PARAGRAPHSTART_ ="):
        header_count = plaintext.count('=')
        if header_count%2 == 0: #Must have an even number of ='s signs
            header_number = int(header_count/2)
            header_text = "="*header_number
            plaintext = plaintext.replace(header_text, " _HEADER"+str(header_number)+"START_ ", 1)
            plaintext = plaintext.replace(header_text, " _HEADER"+str(header_number)+"END_ ", 1)

    return plaintext + " _PARAGRAPHEND_"

def extract_citation_info(external_URLs, wikitext):
    if not external_URLs:
        return []

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
        start_position = reference_starts[index]
        end_position = reference_ends[index]
        citation_info = wikitext[start_position:end_position]
        external_URL = ""
        citation_group = ""

        double_quote_re = r'"([^"]*)"' #Regex pattern to get text between double quote

        if_URL_found = False
        for URL in external_URLs:
            if citation_info.find(URL) != -1: #Check if a known external URL is between <ref> and </ref>
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
    return citations