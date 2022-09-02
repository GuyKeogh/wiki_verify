"""
__description__ = "Raw text processing, by tagging word types with NLTK, and detecting quotes"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

import re

import nltk
from nltk import word_tokenize


def tag_citation_text(citation_words, text, settings):
    if text != "404" and text:
        (
            terms_citations_CD,
            terms_citations_JJ,
            terms_citations_NN,
            terms_citations_NNP,
        ) = get_citation_unique_terms(text, settings)

        citation_words["NN"] = terms_citations_NN
        citation_words["NNP"] = terms_citations_NNP
        citation_words["JJ"] = terms_citations_JJ
        citation_words["CD"] = terms_citations_CD
        citation_words["text"] = text
    return citation_words


def tag_data(text):
    # Extract info
    sentences = nltk.sent_tokenize(text)  # Organize into individual sentences
    data = []
    for sent in sentences:
        data = data + nltk.pos_tag(nltk.word_tokenize(sent))

    tagged_data = []
    index = 0
    for word in data:
        tagged_data.append([word[0], word[1], "none"])
        index += 1
    return tagged_data


def tag_text_of_type(tag_type, data):
    """Only output already tokenised words of specific type that was requested"""
    text_of_tag = []
    index = 0
    for word in data:
        if tag_type in word[1]:
            text_of_tag.append(tuple((word[0], index)))
        index += 1
    return text_of_tag


def set_needed_to_false(tags, settings):
    needed_types = []
    if settings["JJ?"]:
        needed_types.append("JJ")
    if settings["NNP?"]:
        needed_types.append("NNP")
    if settings["NN?"]:
        needed_types.append("NN")
    if settings["CD?"]:
        needed_types.append("CD")

    index = 0
    for tag in tags:
        if tag[1] in needed_types:
            tags[index][2] = "fail"
        index += 1
    return tags


def tag_text_quotes(text):
    """Detects all info in single or double quotes, and outputs all these as strings in a list"""
    matches = re.findall(r"\"(.+?)\"", text)
    return matches


def eval_citation(citation_text):
    sentences = nltk.sent_tokenize(citation_text)  # Organize into individual sentences
    data = []
    for sent in sentences:
        data = data + nltk.pos_tag(nltk.word_tokenize(sent))
    return set(data)


def eval_citation_for_type(citation_text, key):
    """Only output words of specific type stated in key"""
    unique_terms_cite = []
    for word in citation_text:
        if key in word[1]:
            unique_terms_cite.append(word[0])
    return unique_terms_cite


def check_quote_in_text(quote_string, citation_text):
    """Returns True if the input quote is anywhere in the input text, and False if not"""
    return bool(citation_text.find(quote_string) != -1)


def tag_comparisons(text_of_tag, unique_terms_citations_of_tag, data):
    for elem in text_of_tag:
        if data[elem[1]][2] != "pass":
            if elem[0] not in unique_terms_citations_of_tag:
                data[elem[1]][2] = "fail"
            else:
                data[elem[1]][2] = "pass"
    return data


def get_citation_unique_terms(text, settings):
    unique_terms_citations_NNP = []
    unique_terms_citations_NN = []
    unique_terms_citations_JJ = []
    unique_terms_citations_CD = []
    tokenized_citation = eval_citation(text)
    if settings["NN?"]:  # NN (Proper noun, singular)
        citetext_NN = eval_citation_for_type(tokenized_citation, "NN")
        unique_terms_citations_NN = unique_terms_citations_NN + citetext_NN
    if settings["NNP?"]:  # NNP (Proper noun, plural)
        citetext_NNP = eval_citation_for_type(tokenized_citation, "NNP")
        unique_terms_citations_NNP = unique_terms_citations_NNP + citetext_NNP
    if settings["JJ?"]:  # JJ (Adjective)
        citetext_JJ = eval_citation_for_type(tokenized_citation, "JJ")
        unique_terms_citations_JJ = unique_terms_citations_JJ + citetext_JJ
    if settings["CD?"]:  # CD (Cardinal number)
        citetext_CD = eval_citation_for_type(tokenized_citation, "CD")
        unique_terms_citations_CD = unique_terms_citations_CD + citetext_CD
    return (
        unique_terms_citations_CD,
        unique_terms_citations_JJ,
        unique_terms_citations_NN,
        unique_terms_citations_NNP,
    )


def compare_citation_and_text_terms(
    tags,
    unique_terms_citations_CD,
    unique_terms_citations_JJ,
    unique_terms_citations_NN,
    unique_terms_citations_NNP,
    if_detect_NNP=False,
    if_detect_JJ=False,
    if_detect_NN=False,
    if_detect_CD=False,
):
    """Compare unique citation terms of specific type and article text of the same type"""
    text_JJ = []
    text_NN = []
    text_NNP = []
    text_CD = []
    if if_detect_JJ:
        text_JJ = tag_text_of_type("JJ", tags)
        tags = tag_comparisons(text_JJ, unique_terms_citations_JJ, tags)
    if if_detect_NNP:
        text_NNP = tag_text_of_type("NNP", tags)
        tags = tag_comparisons(text_NNP, unique_terms_citations_NNP, tags)
    if if_detect_NN:
        text_NN = tag_text_of_type("NN", tags)
        tags = tag_comparisons(text_NN, unique_terms_citations_NN, tags)
    if if_detect_CD:
        text_CD = tag_text_of_type("CD", tags)
        tags = tag_comparisons(text_CD, unique_terms_citations_CD, tags)
    return tags


def mark_present_quotes(data, quote, if_quote_in_citation):
    """With a citation and a text, marks if it's in that text"""
    quote_in_data_startword = 0
    index = 0
    if_in_quote = False
    quote_list = word_tokenize(quote)  # List of each word in quote
    # Find quote in data
    for word in data:  # find() won't work, as data is in a different format
        if not if_in_quote:
            if word[0] == quote_list[0]:
                if_in_quote = True
                quote_in_data_startword = index
        else:  # If we seem to be in a quote, check it's still true
            if len(quote_list) == (
                index - quote_in_data_startword
            ):  # Fully detected the quote
                for k in range(quote_in_data_startword, index, 1):
                    data[k][1] = "quote"
                    data[k][2] = "pass"
                if_in_quote = False
                quote_in_data_startword = 0
            elif word[0] != quote_list[index - quote_in_data_startword]:
                if_in_quote = False
                quote_in_data_startword = 0
        index += 1
    return data


def detect_quotes_in_string(data, input_text, text_quotes):
    """With every quote and the sole text (used in correction), mark citations present"""
    for quote in text_quotes:
        if_quote_in_citation = check_quote_in_text(quote, input_text)
        data = mark_present_quotes(data, quote, if_quote_in_citation)
    return data


def detect_quotes_in_multiple_texts(data, citation_text, text_quotes):
    """With every quote and all texts, mark all citations that are present"""
    for quote in text_quotes:
        if_quote_in_citation = False
        for citation in citation_text:
            if not if_quote_in_citation:  # Just needs to be in one citation
                if_quote_in_citation = check_quote_in_text(quote, citation)
        data = mark_present_quotes(data, quote, if_quote_in_citation)
    return data
