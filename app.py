"""
__description__ = "Front-end for the web-app"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from datetime import timedelta
from os import cpu_count

from flask import Flask, render_template, request, send_file, session
from flask_session import Session

from src import __metadata__, main
from src.dataparsing import correction
from src.io import filter_title

app = Flask(__name__)

# Session, so data can be held to allow corrections to be made:
app.secret_key = __metadata__.__FLASK_SECRET__
app.config[
    "SESSION_TYPE"
] = "filesystem"  # Store on disk, rather than needing a seperate database or holding client-side (max 4093 bytes)
app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_PERMANENT"] = True  # So thresholds can be used
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    hours=1
)  # Sessions expire after 1 hour
app.config[
    "SESSION_FILE_THRESHOLD"
] = 100  # How many files under flask_session before it starts deleting oldest
server_session = Session(app)


@app.route("/")
def index():
    """Homepage"""
    return render_template("index.html")


@app.route("/correct", methods=["POST"])
def correct():
    """When downloading citations failed, this allows the user to copy-and-paste them and continue"""
    input_text = request.form["correction_text"]

    filtered_name = session["filtered_name"]
    data = session["data"]
    settings = session["settings"]
    language = settings["language"]

    if len(input_text) > 10:
        data["reprocess?"] = True  # Reprocess all data
        data = correction.add_input(input_text, data, settings)

    data = main.main(filtered_name, data, settings)

    URLs_failed = []
    for URL in data["processed_citations"]:
        if URL and URL != "" and data["processed_citations"][URL]["text"] == "404":
            URLs_failed.append(URL)

    return render_template(
        "article.html",
        text=data["HTML_out"],
        page=filtered_name,
        language=language,
        URLs_failed=URLs_failed,
        URLs_failed_count=len(URLs_failed),
    )


@app.route("/article", methods=["POST"])
def article():
    filtered_name = session["filtered_name"]
    data = session["data"]
    settings = session["settings"]
    language = settings["language"]

    if data["segment"] == 0:
        data["segment"] = main.get_first_major_location(data)
    else:
        data["segment"] = main.get_next_major_location(data)
    data = main.main(filtered_name, data, settings)

    URLs_failed = []
    for URL in data["processed_citations"]:
        if URL and URL != "" and data["processed_citations"][URL]["text"] == "404":
            URLs_failed.append(URL)

    html_page = "article.html"
    if len(URLs_failed) != 0:
        html_page = "article_errors.html"

    return render_template(
        html_page,
        text=data["HTML_out"],
        page=filtered_name,
        language=language,
        URLs_failed=URLs_failed,
        URLs_failed_count=len(URLs_failed),
    )


@app.route("/article_start", methods=["POST"])
def article_start():
    """Display the article, including calling the processing of it"""
    # Getting from article:
    POST_name = request.form["page"]  # Article name input by user
    language = request.form["lang"]  # Wikipedia language input by user
    (filtered_name, if_error, error) = filter_title.handle_input_title_language(
        POST_name, language
    )
    if if_error:
        return render_template("index.html", error_message=error)

    # Settings checkboxes. These are only delivered by POST if they are checked,
    # so assume they are False unless delivered:
    if_quote = (
        if_cardinal_number
    ) = if_singular_proper_noun = if_noun = if_adjective = False
    if_attach_all_citations = True
    if request.form.get("ifDefaultSettings"):
        if_quote = if_cardinal_number = if_singular_proper_noun = True
        if_attach_all_citations = False
    else:
        if request.form.get("attach_all_citations_check"):
            if_quote = False
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
    settings = {
        "language": language,
        "quote?": if_quote,
        "CD?": if_cardinal_number,
        "NNP?": if_singular_proper_noun,
        "NN?": if_noun,
        "JJ?": if_adjective,
    }

    # Finished checks
    # Submit to backend:
    data = {  # No data yet
        "segment": 0,
        "segment_last": 0,
        "external_URLs": [],
        "text_segments": [],
        "section_ends": [],
        "citation_data": [],  # Position of each citation in the original wikitext
        "processed_tags": [],
        "processed_citations": dict(),  # Text and tagged words of each citation URL
        "errors": "",
        "if_attach_all_citations": if_attach_all_citations,
        "reprocess?": False,
    }
    data = main.main(filtered_name, data, settings)
    session["filtered_name"] = filtered_name
    session["data"] = data
    session["settings"] = settings

    # Using backend output, render HTML:
    if data["errors"] == "500":  # Generic server error
        return render_template(
            "index.html",
            error_message="The article does not exist (title is case-sensitive), or another error occurred.",
        )
    elif data["errors"] == "_ERROR: problem getting external_URLs_":
        error_message = (
            "A problem occurred grabbing the citations from Wikipedia, please try again. "
            "This error has been recorded."
        )
        return render_template("index.html", error_message=error_message)
    return render_template("article_start.html", page=filtered_name, language=language)


@app.route("/article/<path:POST_name>", methods=["GET"])
def article_named(POST_name):
    """Alternate method of inputting title, allowing /article/<article name> and /article/<Wikipedia page URL>"""
    # Defaults:
    language = "en"
    if_noun = if_adjective = False
    if_quote = if_cardinal_number = if_singular_proper_noun = True

    # /article/<Wikipedia page URL> :
    if ".wikipedia.org/wiki/" in POST_name:
        (language, POST_name) = filter_title.from_url(POST_name)
    (filtered_name, if_error, error) = filter_title.handle_input_title_language(
        POST_name, language
    )
    if if_error:
        return render_template("index.html", error_message=error)

    settings = {
        "language": language,
        "quote?": if_quote,
        "CD?": if_cardinal_number,
        "NNP?": if_singular_proper_noun,
        "NN?": if_noun,
        "JJ?": if_adjective,
    }
    # Finished checks
    # Submit to backend:
    data = {  # No data yet
        "segment": 0,
        "segment_last": 0,
        "external_URLs": [],
        "text_segments": [],
        "section_ends": [],
        "citation_data": [],  # Position of each citation in the original wikitext
        "processed_tags": [],
        "processed_citations": dict(),  # Text and tagged words of each citation URL
        "errors": "",
        "if_attach_all_citations": False,
        "reprocess?": False,
    }
    data = main.main(filtered_name, data, settings)
    filtered_name = filtered_name.replace(
        "_", " "
    )  # Remove possible _'s in title before showing on screen
    session["filtered_name"] = filtered_name
    session["data"] = data
    session["settings"] = settings

    # Using backend output, render HTML:
    if data["errors"] == "500":  # Generic server error
        return render_template(
            "index.html",
            error_message="The article does not exist (title is case-sensitive), or another error occurred.",
        )
    elif data["errors"] == "_ERROR: problem getting external_URLs_":
        error_message = (
            "A problem occurred grabbing the citations from Wikipedia, please try again. "
            "This error has been recorded."
        )
        return render_template("index.html", error_message=error_message)
    return render_template("article.html", page=filtered_name, language=language)


@app.route("/robots.txt")
def robots():
    """Allow the site to be indexed. Send_file delivers the exact .txt with formatting"""
    return send_file("templates/robots.txt")


if __name__ == "__main__":
    """Start the server"""
    if __metadata__.__IF_PRODUCTION__:
        print("Starting production server...")
        from waitress import serve

        serve(app, host="localhost", port=8080, url_scheme="https", threads=cpu_count())
    else:
        print("Starting debug server...")
        app.run(debug=True, port=8080)
