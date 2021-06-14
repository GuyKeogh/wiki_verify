from flask import Flask, request, render_template
from os import urandom
import main

app = Flask(__name__)
app.config["SECRET_KEY"] = str(urandom(24));

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/article', methods = ["POST"])
def article():
    POST_name = request.form["name"]
    html_output = main.main(POST_name)
    return render_template("article.html", text = html_output, name = POST_name)

if __name__ == '__main__':
    if_production = True
    if(if_production==True):
        print("Starting production server...")
        from waitress import serve
        serve(app, host="localhost", port=5000)
    else:
        print("Starting debug server...")
        app.run(debug = True, port=5000)
