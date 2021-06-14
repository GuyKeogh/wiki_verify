# Wikipedia article factchecker

## Introduction
This is a Python application to assist in fact-checking Wikipedia articles by automating comparisons between the Wikipedia article text, and links and citations within that article. This can be hosted (locally by default), or used as a standalone Python application.

## To run:
* (OPTIONAL, but recommended) Install and use a virtualenv (not included)
* Run 'pip3 install -r requirements.txt'
* Run 'python app.py' to use the locally hosted web app, or 'python standalone.py' for the Python application
* (WEB APP) Go to 'http://localhost:5000' in a browser on the same computer
* Enter a valid Wikipedia article name and submit

## Usage

When the above is followed after a few seconds a HTML page will open. With the web app a redirect will be made to the created page once it is generated, and with the standalone app a file 'article.html' will be generated in the same directory and opened in the default web browser.

Text that needs to be checked is marked in red, while text that appears to be fine is marked in green. If there is no marking that text has not been checked. Marked text can be hovered over to see information about the text.

## Current comparisons
The following comparisons are made between the Wikipedia article and its citations:
* Proper nouns, i.e. a specifically named person/place/thing
* Quotations

These comparisons work especially well for biographies.

If these are used in the article but not present in any links or citations in the article, and the citation was properly downloaded, then that text might be spelled differently, uncited, or outright fabricated.

## Current limitations
* This is not definitive. It flags things that need double checking to make the fact-checking process easier.
* This tool does not translate. If citations are in a different language to the article the comparison will not work.

As this is currently a proof-of-concept tool:
* It doesn't have rate limiting or multithreading
* This currently only automatically extracts the text in raw HTML, and does not handle PDFs, redirects, server-side refusals to deliver text, etc. If an issue is detected, currently only the **standalone** program will ask you to copy-and-paste this text which will otherwise be ignored.
* Use it on small/medium sized articles only as it downloads and makes comparisons against the plain-HTML every single external link in that article.

## requirements.txt
To download page JSON and HTML, and extract the raw text from these:
* requests
* beautifulsoup4

Natural language processing to extract word types, where the lists of each type are then compared:
* nltk

For the standalone app only:
* webbrowser

For the web app only:
* flask
* waitress