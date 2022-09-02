def strip_end_sections(text):
    """Strip useless parts at end (refs, see also, etc)"""
    references_start = text.rfind("References")
    see_also_start = text.rfind("See also")
    external_links_start = text.rfind("External links")
    further_reading_start = text.rfind("Further reading")

    end_of_document = references_start
    if see_also_start < end_of_document and see_also_start != -1:
        end_of_document = see_also_start
    if external_links_start < end_of_document and external_links_start != -1:
        end_of_document = external_links_start
    if further_reading_start < end_of_document and further_reading_start != -1:
        end_of_document = further_reading_start

    if end_of_document != -1:
        text = text[:end_of_document]
    return text
