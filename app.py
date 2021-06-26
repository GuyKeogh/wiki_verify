"""
__description__ = "Front-end for the web-app"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from datetime import datetime
from os import urandom, cpu_count
from flask import Flask, session, request, render_template, send_file
from flask_session import Session
from source import main, filter_title, __metadata__, correction

app = Flask(__name__)

#Session, so data can be held to allow corrections to be made:
app.secret_key = str(urandom(24))
app.config['SESSION_TYPE'] = 'filesystem' #Store on disk, rather than needing a seperate database or holding client-side (max 4093 bytes)
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_PERMANENT'] = True #So thresholds can be used
app.config['PERMANENT_SESSION_LIFETIME'] = __metadata__.CORRECTION_RETENTION_TIME*60
app.config['SESSION_FILE_THRESHOLD'] = 100 #How many files under flask_session before it starts deleting oldest
server_session = Session(app)

@app.route('/')
def index():
    """Homepage"""
    return render_template("index.html")

@app.route('/correct', methods = ["POST"])
def correct():
    """When downloading citations failed, this allows the user to copy-and-paste them and continue"""
    POST_session = request.form["session_ID"]
    try:
        (article_title, data, text_quotes, settings, session_creation_date) = session[POST_session]
        (language, if_detect_quote, if_detect_NNP, if_detect_JJ, if_detect_NN, if_detect_CD) = settings
        
        input_text = request.form["correction_text"]
        #Feed back to a more streamlined function for the absolute final output:
        html_output = correction.correction(article_title,
                                            data,
                                            input_text,
                                            text_quotes,
                                            language=language,
                                            if_detect_quote=if_detect_quote,
                                            if_detect_NNP=if_detect_NNP,
                                            if_detect_JJ=if_detect_JJ,
                                            if_detect_NN=if_detect_NN,
                                            if_detect_CD=if_detect_CD)

        return render_template("article.html",
                               text=html_output,
                               page=article_title,
                               language=language)
    except:
        error_message = "The session has expired."
        return render_template("index.html", error_message=error_message)

@app.route('/article', methods = ["POST"])
def article():
    """Display the article, including calling the processing of it"""
    #Getting from article:
    if_quote = if_cardinal_number = if_singular_proper_noun = if_noun = if_adjective = False
    
    POST_name = request.form["page"] #Article name input by user
    language = request.form["lang"] #Wikipedia language input by user

    #Settings checkboxes. These are only delivered by POST if they are checked, so assume they are False unless delivered:
    if request.form.get("ifDefaultSettings"):
        if_quote = if_cardinal_number = if_singular_proper_noun = True
    else:
        if request.form.get("quote_check"):
            if_quote = True
        if request.form.get("CD_check"):
            if_cardinal_number = True
        if request.form.get("NNP_check"):
            if_singular_proper_noun = True
        if request.form.get("NN_check"):
            if_noun = True
        if request.form.get("JJ_check"):
            if_adjective = True

    filtered_name = filter_title.filter_title(POST_name) #Removes whitespace, etc

    #Filter bad inputs:
    title_length = len(filtered_name)
    if title_length>=256: #Article names must be less than 256 bytes
        return render_template("index.html",
                               error_message="An article cannot have this title (too long).")
    if title_length==0: #Nothing entered
        return render_template("index.html",
                               error_message="No title entered.")
    if filter_title.if_title_invalid_symbol_use(filtered_name): #Problematic symbol use
        return render_template("index.html",
                               error_message="An article cannot have this title (invalid symbol use).")

    #Language checks:
    if language!="en" and language !="simple":
        return render_template("index.html", error_message = "Language not supported.")

    #Finished checks
    #Submit to backend:
    output = main.main(article_title=filtered_name,
                        language=language,
                        if_ignore_URL_error=True,
                        if_detect_quote=if_quote,
                        if_detect_CD=if_cardinal_number,
                        if_detect_NNP=if_singular_proper_noun,
                        if_detect_NN=if_noun,
                        if_detect_JJ=if_adjective
                        )
    (html_output,external_URLs_failed,data,text_quotes) = output
    fail_count = len(external_URLs_failed)
    
    if fail_count>0: #Create session to request copy-and-paste of failed URLs
        settings = (language,if_quote,
                    if_singular_proper_noun,
                    if_adjective,
                    if_noun,
                    if_cardinal_number
                    )
        session_ID = str(urandom(24))
        session_elem = (filtered_name,
                        data,
                        text_quotes,
                        settings,
                        datetime.now()
                        )
        session[session_ID] = session_elem
        return render_template("article_errors.html",
                               text=html_output,
                               page=filtered_name,
                               language=language,
                               session_ID=session_ID,
                               error_count=fail_count,
                               URLs_failed=external_URLs_failed
                               )
    #Using backend output, render HTML:
    if(html_output=="500"): #Generic server error
        return render_template("index.html",
                               error_message = "The article does not exist (title is case-sensitive), or another error occurred.")
    elif(html_output=="_ERROR: too many external_URLs_"): 
        max_URL = str(__metadata__.__WEB_EXTERNAL_URL_LIMIT__)
        error_message = "There are too many citations in the article (over "+max_URL+"). Note: this limit does not apply with the desktop program."
        return render_template("index.html",
                               error_message = error_message)
    else: #Everything is fine
        return render_template("article.html",
                               text=html_output,
                               page=filtered_name,
                               language=language)
@app.route('/article/<POST_name>')
def article_named(POST_name):
    filtered_name = filter_title.filter_title(POST_name) #Removes whitespace, etc

    #Filter bad inputs:
    title_length = len(filtered_name)
    if title_length>=256: #Article names must be less than 256 bytes
        return render_template("index.html",
                               error_message="An article cannot have this title (too long).")
    if title_length==0: #Nothing entered
        return render_template("index.html",
                               error_message="No title entered.")
    if filter_title.if_title_invalid_symbol_use(filtered_name): #Problematic symbol use
        return render_template("index.html",
                               error_message="An article cannot have this title (invalid symbol use).")
    
    if_noun = if_adjective = False
    if_quote = if_cardinal_number = if_singular_proper_noun = True
    language = "en"

    #Finished checks
    #Submit to backend:
    output = main.main(article_title=filtered_name,
                        language=language,
                        if_ignore_URL_error=True,
                        if_detect_quote=if_quote,
                        if_detect_CD=if_cardinal_number,
                        if_detect_NNP=if_singular_proper_noun,
                        if_detect_NN=if_noun,
                        if_detect_JJ=if_adjective
                        )
    (html_output,external_URLs_failed,data,text_quotes) = output
    fail_count = len(external_URLs_failed)
    
    if fail_count>0: #Create session to request copy-and-paste of failed URLs
        settings = (language,if_quote,
                    if_singular_proper_noun,
                    if_adjective,
                    if_noun,
                    if_cardinal_number
                    )
        session_ID = str(urandom(24))
        session_elem = (filtered_name,
                        data,
                        text_quotes,
                        settings,
                        datetime.now()
                        )
        session[session_ID] = session_elem
        return render_template("article_errors.html",
                               text=html_output,
                               page=filtered_name,
                               language=language,
                               session_ID=session_ID,
                               error_count=fail_count,
                               URLs_failed=external_URLs_failed
                               )
    #Using backend output, render HTML:
    if(html_output=="500"): #Generic server error
        return render_template("index.html",
                               error_message = "The article does not exist (title is case-sensitive), or another error occurred.")
    elif(html_output=="_ERROR: too many external_URLs_"): 
        max_URL = str(__metadata__.__WEB_EXTERNAL_URL_LIMIT__)
        error_message = "There are too many citations in the article (over "+max_URL+"). Note: this limit does not apply with the desktop program."
        return render_template("index.html",
                               error_message = error_message)
    else: #Everything is fine
        return render_template("article.html",
                               text=html_output,
                               page=filtered_name,
                               language=language)

@app.route('/robots.txt')
def robots():
    """Allow the site to be indexed. Send_file delivers the exact .txt with formatting"""
    return send_file("templates/robots.txt")

if __name__ == '__main__':
    """Start the server"""
    if __metadata__.__IF_PRODUCTION__:
        print("Starting production server...")
        from waitress import serve
        serve(app, host="localhost", port=8080, url_scheme="https",threads=cpu_count())
    else:
        print("Starting debug server...")
        app.run(debug = True, port=8080)
