"""
__description__ = "Front-end for the web-app"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from datetime import datetime
from os import urandom, cpu_count
from flask import Flask, request, render_template, send_file
from source import main, filter_title, __metadata__, correction, analytics, session

app = Flask(__name__)
app.config["SECRET_KEY"] = str(urandom(24));

@app.route('/')
def index():
    """Homepage"""
    return render_template("index.html")

@app.route('/correct', methods = ["POST"])
def correct():
    """When downloading citations failed, this allows the user to copy-and-paste them and continue"""
    POST_session = request.form["session_ID"]
    if_session_exists = False
    session_index = 0
    #Check if the session exists:
    for elem in session.sessions:
        if elem[0]==POST_session:
            if_session_exists = True
            break
        session_index+=1

    if if_session_exists:
        input_text = request.form["correction_text"]
        (session_ID,article_title,data,text_quotes,settings,session_creation_date) = session.sessions[session_index]
        (language,if_detect_quote,if_detect_NNP,if_detect_JJ,if_detect_NN,if_detect_CD) = settings
        session.sessions.pop(session_index) #As the session was used, delete it
        analytics.analytics_total_used_session_time += (datetime.now() - session_creation_date).total_seconds() / 60.0
        
        #Feed back to a more streamlined function for the absolute final output:
        html_output = correction.correction(article_title,
                                            data,
                                            input_text,
                                            text_quotes,
                                            language="en",
                                            if_detect_quote=if_detect_quote,
                                            if_detect_NNP=if_detect_NNP,
                                            if_detect_JJ=if_detect_JJ,
                                            if_detect_NN=if_detect_NN,
                                            if_detect_CD=if_detect_CD)

        return render_template("article.html",
                               text=html_output,
                               page=article_title,
                               language=language)
    else:
        error_message = "The session has expired (over "+str(__metadata__.correction_retention_time)+" minutes since request)."
        return render_template("index.html", error_message=error_message)

@app.route('/article', methods = ["POST"])
def article():
    """Display the article, including calling the processing of it"""
    #Maintenance:
    analytics.analytics_submits[analytics.analytics_hours_since_init()] += 1
    session.check_session_expiration()
    
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
    if language!="en":
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
    
    if fail_count>0: #Create session
        analytics.analytics_total_sessions+=1
        settings = (language,if_quote,
                    if_singular_proper_noun,
                    if_adjective,
                    if_noun,
                    if_cardinal_number
                    )
        session_elem = (str(urandom(24)),
                        filtered_name,
                        data,
                        text_quotes,
                        settings,
                        datetime.now()
                        )
        session.sessions.append(session_elem)
        return render_template("article_errors.html",
                               text=html_output,
                               page=filtered_name,
                               language=language,
                               session_ID=session_elem[0],
                               error_count=fail_count,
                               URLs_failed=external_URLs_failed
                               )
    #Using backend output, render HTML:
    if(html_output!="500"):
        analytics.analytics_successes[analytics.analytics_hours_since_init()] += 1
        return render_template("article.html",
                               text=html_output,
                               page=filtered_name,
                               language=language)
    else: #Generic error
        return render_template("index.html",
                               error_message = "The article does not exist (title is case-sensitive), or another error occurred.")

@app.route('/robots.txt')
def robots():
    """Allow the site to be indexed. Send_file delivers the exact .txt with formatting"""
    return send_file("templates/robots.txt")

@app.route('/dashboard')
def dashboard():
    """Info about how the program is used to help with optimisation"""
    session.check_session_expiration()
    return render_template("dashboard.html",
                           retention_hours=analytics.ANALYTICS_RETENTION_HOURS,
                           request_time=datetime.now(),
                           submits=analytics.analytics_submits,
                           successes=analytics.analytics_successes,
                           session_count=len(session.sessions),
                           session_retention=__metadata__.CORRECTION_RETENTION_TIME,
                           total_sessions=analytics.analytics_total_sessions,
                           unused_sessions=analytics.analytics_unused_sessions,
                           total_used_session_time=analytics.analytics_total_used_session_time
                           )


if __name__ == '__main__':
    """Start the server"""
    if __metadata__.__IF_PRODUCTION__:
        print("Starting production server...")
        from waitress import serve
        serve(app, host="localhost", port=8080, url_scheme="https",threads=cpu_count())
    else:
        print("Starting debug server...")
        app.run(debug = True, port=8080)
