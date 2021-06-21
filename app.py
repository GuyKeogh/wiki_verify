"""
__description__ = "Front-end for the web-app"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from flask import Flask, request, render_template
from os import urandom, cpu_count
from source import main
from source import filter_title
from source import __metadata__

app = Flask(__name__)
app.config["SECRET_KEY"] = str(urandom(24));

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/robots.txt')
def robots():
	return render_template("robots.txt")

@app.route('/article', methods = ["POST"])
def article():
    POST_if_quote = False
    POST_if_CD = False
    POST_if_NNP = False
    POST_if_NN = False
    POST_if_JJ = False
    
    POST_name = request.form["page"] #Article name input by user
    POST_language = request.form["lang"] #Wikipedia language input by user
    
    #Settings checkboxes. These are only delivered by POST if they are checked, so assume they are False unless delivered:
    if(request.form.get("ifDefaultSettings")):
        POST_if_quote = True
        POST_if_CD = True
        POST_if_NNP = True
    else:
        if(request.form.get("quote_check")):
            POST_if_quote = True
        if(request.form.get("CD_check")):
            POST_if_CD = True
        if(request.form.get("NNP_check")):
            POST_if_NNP = True
        if(request.form.get("NN_check")):
            POST_if_NN = True
        if(request.form.get("JJ_check")):
            POST_if_JJ = True
        
    filtered_name = filter_title.filter_title(POST_name) #Removes whitespace, etc
    
    #Filter bad inputs:
    #Checks on article name from https://en.wikipedia.org/wiki/Wikipedia:Naming_conventions_(technical_restrictions) :
    title_length = len(filtered_name)
    if(title_length>=256): #Article names must be less than 256 bytes
        return render_template("index.html", error_message = "An article cannot have this title (too long).")
    if(title_length==0): #Nothing entered
        return render_template("index.html", error_message = "No title entered.")
    if(filter_title.if_title_invalid_symbol_use(filtered_name)): #Problematic symbol use
        return render_template("index.html", error_message = "An article cannot have this title (invalid symbol use).")
    
    #Language checks:
    if(POST_language!="en"):
        return render_template("index.html", error_message = "Language not supported.")
    
    #Finished checks
    #Submit to backend:
    html_output = main.main(article_title = filtered_name, language=POST_language, if_ignore_URL_error=True,
                            if_detect_quote=POST_if_quote,if_detect_CD=POST_if_CD,if_detect_NNP=POST_if_NNP,
                            if_detect_NN=POST_if_NN,if_detect_JJ=POST_if_JJ)
    
    #Using backend output, render HTML:
    if(html_output!="500"):
        return render_template("article.html", text = html_output, page = filtered_name, language = POST_language)
    else: #Generic error
        return render_template("index.html", error_message = "The article does not exist (title is case-sensitive), or another error occurred.")

if __name__ == '__main__':
    if_production = __metadata__.__if_production__ #Get if the program is in production from file /source/__metadata__.py
    if(if_production==True):
        print("Starting production server...")
        from waitress import serve
        serve(app, host="localhost", port=8080, url_scheme="https",threads=cpu_count())
    else:
        print("Starting debug server...")
        app.run(debug = True, port=8080)
