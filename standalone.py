import webbrowser
import programIO
import main

def main_standalone():
    article_title = input("Enter the article title: ")
    
    html_output = main.main(article_title)
    programIO.write_file(html_output,"article.html")
    webbrowser.open("article.html")

main_standalone()