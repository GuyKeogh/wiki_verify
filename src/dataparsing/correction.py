"""
__description__ = "Handles user-inputted URL text from failed URLs to verify information for final"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from source.dataparsing import text_tagging


def add_input(input_text, data, settings):
    processed_citations = data["processed_citations"]
    URL_indexes = dict()

    for external_URL in processed_citations:
        if not external_URL or external_URL == "":
            continue

        position = input_text.find(external_URL)
        if position != -1:  # If some URL on the page is within the user input
            URL_indexes.update(
                {position + len(external_URL): external_URL}
            )  # Save the start position of the URL and the URL itself

    if not URL_indexes:  # No URLs supplied
        data["reprocess?"] = False
    else:
        # Order the indexes:
        URL_indexes_ordered = []
        for index in URL_indexes:
            URL_indexes_ordered.append(
                index
            )  # Get the index from the dictionary with structure {index: URL}
        URL_indexes_ordered = sorted(URL_indexes_ordered)

        # Add the inputted text to its value in the dictionary of citations and their data:
        indexes_index = 0
        for position_start in URL_indexes_ordered:
            citation_words = {"text": "", "CD": [], "JJ": [], "NN": [], "NNP": []}
            # We already have the start index, so find the end index:
            position_end = 0
            if indexes_index + 1 < len(URL_indexes_ordered):
                position_end = URL_indexes_ordered[
                    indexes_index + 1
                ]  # Start of next URL in list
            else:
                position_end = len(input_text)  # End of inputted text - no more URLs
            # Using the start and end indexes, find the relevant text:
            text = input_text[position_start:position_end]

            # Get the associated URL via a dictionary lookup with the first index:
            external_URL = URL_indexes[position_start]

            # Finally, do all the processing, adding the user-inputted text to the processed citations:
            citation_words = text_tagging.tag_citation_text(
                citation_words, text, settings
            )
            processed_citations[external_URL] = citation_words
            indexes_index += 1

    data["processed_citations"] = processed_citations
    return data
