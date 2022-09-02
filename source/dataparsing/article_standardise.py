"""
__description__ = "Standardises downloaded Wikipedia article to a consistent format that can be 
processed better such as making punctuation fixes, stripping end-sections, etc."
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""


def strip_end_sections(text):
    """Strip useless parts at end (refs, see also, etc)"""
    References_start = text.rfind("References")
    See_also_start = text.rfind("See also")
    External_links_start = text.rfind("External links")
    Further_reading_start = text.rfind("Further reading")

    end_of_document = References_start
    if See_also_start < end_of_document and See_also_start != -1:
        end_of_document = See_also_start
    if External_links_start < end_of_document and External_links_start != -1:
        end_of_document = External_links_start
    if Further_reading_start < end_of_document and Further_reading_start != -1:
        end_of_document = Further_reading_start

    if end_of_document != -1:
        text = text[:end_of_document]

    return text
