# Wikipedia article factchecker

The tool can be accessed online at https://verify.toolforge.org/

## Introduction

This is a Python application which uses a heuristic approach to assist in fact-checking Wikipedia articles by automating comparisons between the Wikipedia article text, and links and citations within that article. This can be used via the
website, or locally hosted on your own computer.

### Methodology

The application ensures proper nouns (explicitly named people/places/things) and numbers used in an article are present within any citation or external link within the page. This is easily doable as proper nouns and numbers cannot be
modified much in language, a contrast to adjectives, verbs, etc, and so proper nouns and numbers can typically be directly compared for between different texts. This ensures the article matches the general information within the source
text.

Additionally, quotes (any text enclosed by single or double quotes) are checked to see if they are present in any citation or external link.

## To run locally:

* Download and unzip the latest release: https://github.com/GuyKeogh/wiki_verify/releases/
* Have Python 3.7 or above installed
* Install Poetry using the install instructions https://python-poetry.org/docs/

From the command line, when in the directory the files have been saved:

* Create the Poetry environment. PyCharm can detect the `pyproject.toml` automatically and install from this.
* Activate the Poetry environment.
* Run `python`, then enter `import nltk` and enter both `nltk.download('punkt')` and `nltk.download('averaged_perceptron_tagger')`. Enter `exit()` to exit the Python shell.
* Run `python3 app.py` to use the locally hosted web app.
* Go to http://localhost:8080 in a browser on the same computer
* Enter a valid Wikipedia article name and submit

## Usage

When the above is followed after a few seconds a redirect will be made to the created page once it is generated. To process more of the article, click 'Next paragraph(s)', and additional text will be processed.

Text that needs to be checked is highlighted in yellow and underlined, while text that appears to be fine is marked in green. These colours were chosen for colourblind-friendliness. If there is no marking that text has not been checked.
Marked text can be hovered over to see information about the text.

For articles with relatively few citations, consider unchecking "Require citation to be in the same paragraph as the text being verified" under default settings; with this unchecked, the text of every citation will be downloaded, processed,
and applied to every paragraph upon submission, instead of citation texts being downloaded only as they're demanded and applied only to the paragraphs the citation is used within. Unchecking this will result in slower initial loading, and
this cannot be done for articles with many citations due to the time required to download and process these in one go.

## Current limitations

* This is not definitive. It flags things that need double checking to make the fact-checking process easier.
* This tool does not translate. If citations are in a different language to the article the comparison might not work, so valid text might be marked as needing to be checked.
* It makes direct comparisons. If a word is spelled differently between the texts or a quotation has a clarification inside it that's not present in the source text, then it will be flagged as needing to be checked.
* This currently only automatically extracts the text in raw HTML, and does not handle PDFs, redirects, server-side refusals to deliver text, etc. If an issue is detected, the opportunity is given to copy-and-paste this text.

## requirements.txt

To download page JSON and HTML, and extract the raw text from these:

* requests
* beautifulsoup4

Natural language processing to extract word types, where the lists of each type are then compared:

* nltk

To strip templates, images, etc, from wikitext:

* wikitextparser

To deliver the web app:

* flask
* waitress

To allow copy-and-pasting of content in URLs which could not be downloaded:

* flask_session
