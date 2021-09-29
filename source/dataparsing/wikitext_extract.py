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

def pair_brackets(link_starts, link_ends):
    """When brackets are within each other, e.g. [[file:photo.jpg|... | text leading to [[link]]]],
    pairing the first [[ with the next ]] doesn't work; this function returns the proper pairing"""
    index = 0
    for bracket in link_starts:
        if(index+1 < len(link_starts) and index+1 < len(link_ends)):
            if link_starts[index+1] < link_ends[index]:
                final_end_pair = link_ends[index]
                link_ends[index] = link_ends[index+1]
                link_ends[index+1] = final_end_pair
        index+=1
    return tuple((link_starts, link_ends))

def wikitext_to_plaintext(wikitext):
    import re
    from wikitextparser import remove_markup
    plaintext = "_PARAGRAPHSTART_ "+wikitext #Each segment is its own paragraph, so add tag

    #Bold text:
    quantity = int(len([m.start() for m in re.finditer("'''", plaintext)])/2)
    for i in range(0, quantity):
        plaintext = plaintext.replace("'''", "_BOLDSTART_ ", 1).replace("'''", " _BOLDEND_", 1)
    
    #Italic text:
    quantity = int(len([m.start() for m in re.finditer("''", plaintext)])/2)
    for i in range(0, quantity):
        plaintext = plaintext.replace("''", " _ITALICSTART_ ", 1).replace("''", " _ITALICEND_ ", 1)

    #Replace headers with tags:
    if plaintext.startswith("_PARAGRAPHSTART_ \n="):
        header_count = plaintext.count('=')
        if header_count%2 == 0: #Must have an even number of ='s signs
            header_number = int(header_count/2)
            header_text = "="*header_number
            plaintext = plaintext.replace(header_text, " _HEADER"+str(header_number)+"START_ ", 1)
            plaintext = plaintext.replace(header_text, " _HEADER"+str(header_number)+"END_ ", 1)
    
    print(plaintext)

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
    
    plaintext = remove_markup(plaintext)
    return plaintext + " _PARAGRAPHEND_"

def extract_citation_info(external_URLs, wikitext):
    if not external_URLs:
        return []

    import re

    newline_indexes = [m.start() for m in re.finditer('\n', wikitext)] #Get position of every \n in the text, as these are useful reference points

    #First, find the start locations of every reference:
    reference_starts = [m.start() for m in re.finditer('<ref', wikitext)] #Both normal cites and labels start with '<ref'
    reference_ends = [m.start() for m in re.finditer('</ref>|/>', wikitext)] #Normal cites end in '</ref>', but labels end in '/>'

    # Ensure that all reference start indexes are before the end indexes (e.g. '/>' in '<br />' mixed in), and remove offending end indexes:
    if len(reference_ends) > len(reference_starts):
        index = 0
        while index < len(reference_ends):
            if reference_ends[index] < reference_starts[index]:
                reference_ends.pop(index)
            index+=1

    citations = [] #List of tuples, with structure: (start_position, end_position, URL, how many newlines before start, label (optional))
    label_dictionary = {};

    #Check which external_URL falls between the reference start and ends:
    double_quote_re = r'"([^"]*)"' #Regex pattern to get text between double quote
    index = 0
    for reference in reference_starts:
        start_position = reference_starts[index]
        end_position = reference_ends[index]
        citation_info = wikitext[start_position:end_position]
        external_URL = ""
        citation_group = ""
        if_URL_found = False

        for URL in external_URLs:
            if not URL:
                continue
            if citation_info.find(URL) != -1: #Check if a known external URL is between <ref> and </ref>
                if_URL_found = True
                external_URL = URL

                label_name_index = citation_info.find('name=')
                if label_name_index != -1: #Citation contains a group name too; the URL can then be used for citations with the same label
                    if '"' in citation_info: #E.g. if the ref template is <ref name="whatever">, remove the quotes
                        citation_group_quote = re.search(double_quote_re, citation_info[label_name_index:]).group() #Find first double quote after name=
                        citation_group = citation_group_quote[1:-1] #Remove the double quotes (first and last characters)
                        label_dictionary.update({citation_group: URL})
                    else:
                        label_dictionary.update({citation_info[label_name_index:]: URL})
                break

        if not if_URL_found and URL: #No known external URL found in the template; search for a group instead
            label_name_index = citation_info.find('name=')
            if label_name_index != -1:
                citation_group = ""
                if '"' in citation_info: #E.g. if the ref template is <ref name="whatever">, remove the quotes
                    citation_group_quote = re.search(double_quote_re, citation_info[label_name_index:]).group() #Find first double quote after name=
                    citation_group = citation_group_quote[1:-1] #We now have the group name, so we can look it up in the dictionary once that's fully made
                else:
                    citation_group = citation_info[label_name_index:].replace("name=", "")
                label_dictionary.update({citation_group: URL})
        
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
        
        updated_citation_tuple = (start, end, cite_URL, cite_index, cite_label)
        citations[index] = updated_citation_tuple
        index+=1
    
    return citations