import webbrowser
import programIO
import main

def main_standalone():
    article_title = input("Enter the article title: ")
    
    html_output = main.main(article_title,if_ignore_URL_error=False)
    if(html_output!="500"):
        programIO.write_file(html_output,"article.html")
        webbrowser.open("article.html")
    else:
        print("The article does not exist, or another error occurred.")

main_standalone()