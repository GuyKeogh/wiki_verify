"""
__description__ = "Front-end for the web-app"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

from flask import Flask, request, render_template
from os import urandom
from source import main
from source import filter_title

app = Flask(__name__)
app.config["SECRET_KEY"] = str(urandom(24));

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/article', methods = ["POST"])
def article():
    POST_name = request.form["name"] #The article name inputted by the user
    
    #Filter bad inputs, from least to most computationally costly:
    #Checks on article name from https://en.wikipedia.org/wiki/Wikipedia:Naming_conventions_(technical_restrictions) :
    title_length = len(POST_name)
    if(title_length>=256): #Article names must be less than 256 bytes
        return render_template("index.html", error_message = "An article cannot have this title (too long).")
    if(title_length==0): #Nothing entered
        return render_template("index.html", error_message = "No title entered.")
    if(filter_title.if_title_invalid_symbol_use(POST_name)): #Problematic symbol use
        return render_template("index.html", error_message = "An article cannot have this title (invalid symbol use).")
    
    #Finished checks
    #Submit to backend:
    html_output = main.main(filter_title.filter_title(POST_name), if_ignore_URL_error=True)
    
    #Using backend output, render HTML:
    if(html_output!="500"):
        return render_template("article.html", text = html_output, name = POST_name)
    else: #Generic error
        return render_template("index.html", error_message = "The article does not exist, or another error occurred.")

if __name__ == '__main__':
    if_production = True
    if(if_production==True):
        print("Starting production server...")
        from waitress import serve
        serve(app, host="localhost", port=5000)
    else:
        print("Starting debug server...")
        app.run(debug = True, port=5000)
