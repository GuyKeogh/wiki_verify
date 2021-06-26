# Wikipedia article factchecker
The tool can be accessed online at https://verify.toolforge.org/

## Introduction
This is a Python application which uses a heuristic approach to assist in fact-checking Wikipedia articles by automating comparisons between the Wikipedia article text, and links and citations within that article. This can be hosted (locally by default), or used as a standalone Python application.

### Methodology
The application ensures proper nouns (explicitly named people/places/things) and numbers used in an article are present within any citation or external link within the page. This is easily doable as proper nouns and numbers cannot be modified much in language, a contrast to adjectives, verbs, etc, and so proper nouns and numbers can typically be directly compared for between different texts. This ensures the article matches the general information within the source text.

Additionally, quotes (any text enclosed by single or double quotes) are checked to see if they are present in any citation or external link.

## To run:
* Have Python 3 installed
* (OPTIONAL, but recommended) Install and use a virtualenv (not included)

When in the directory the files have been saved:
* Run 'pip3 install -r requirements.txt'
* Run 'python', 'import nltk' and enter both 'nltk.download('punkt')' and 'nltk.download('averaged_perceptron_tagger')'
* Run 'python app.py' to use the locally hosted web app, or 'python standalone.py' for the Python application
* (WEB APP) Go to 'http://localhost:8080' in a browser on the same computer
* Enter a valid Wikipedia article name and submit

## Usage

When the above is followed after a few seconds a HTML page will open. With the web app a redirect will be made to the created page once it is generated, and with the standalone app a file 'article.html' will be generated in the same directory and opened in the default web browser.

Text that needs to be checked is marked in red, while text that appears to be fine is marked in green. If there is no marking that text has not been checked. Marked text can be hovered over to see information about the text.

## Current limitations
* This is not definitive. It flags things that need double checking to make the fact-checking process easier.
* This tool does not translate. If citations are in a different language to the article the comparison might not work, so valid text might be marked as needing to be checked.
* It makes direct comparisons. If a word is spelled differently between the texts or a quotation has a clarification inside it that's not present in the source text, then it will be flagged as needing to be checked.
* This currently only automatically extracts the text in raw HTML, and does not handle PDFs, redirects, server-side refusals to deliver text, etc. If an issue is detected, the opportunity is given to copy-and-paste this text.

## requirements.txt
To download page JSON and HTML, and extract the raw text from these:
* requests
* beautifulsoup4

To allow copy-and-pasting of content in URLs which could not be downloaded:
* flask_session

Natural language processing to extract word types, where the lists of each type are then compared:
* nltk

For the standalone app only:
* webbrowser

For the web app only:
* flask
* waitress
