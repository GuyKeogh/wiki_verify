"""
__description__ = "Front-end for standalone program"
__author__ = "Guy Keogh"
__license__ = "BSD 2-Clause"
"""

import webbrowser
from source import main, filter_title

def main_standalone():
    """Main function for standalone program"""
    if_continue = True
    while if_continue:
        article_title = input("Enter the article title: ")

        if if_title_valid(article_title):
            output = main.main(filter_title.filter_title(article_title),if_ignore_URL_error=False)
            (html_output,external_URLs_failed,data,text_quotes) = output
            #Process backend output:
            if html_output!="500":
                #Start:
                write_file("<!DOCTYPE html><html>","article.html")
                #HTML head:
                append_to_file("<head><meta charset='UTF-8'><link rel='stylesheet' type='text/css' href='static/bootstrap.css'></head>","article.html")
                #HTML body:
                append_to_file("<body>","article.html")
                append_to_file("<center><h2>"+article_title+"</h2></center>","article.html")
                append_to_file(html_output,"article.html")
                append_to_file("</body>","article.html")
                
                #End:
                append_to_file("</html>","article.html")
                
                #Open in default browser:
                webbrowser.open("article.html")
            else:
                print("The article does not exist, or another error occurred.")
        else:
            print("Cancelling...")

        if_continue = optional_input("-------\n\nDo you wish to run the program again? Yes or No: ")

def if_title_valid(title):
    """Checks on article title to ensure it's possible for it to exist"""
    title_length = len(title)
    if title_length>=256: #Article names must be less than 256 bytes
        print("An article cannot have this title (too long).")
        return False
    if title_length==0: #Nothing entered
        print("No title entered.")
        return False
    if filter_title.if_title_invalid_symbol_use(title): #Problematic symbol use
        print("An article cannot have this title (invalid symbol use).")
        return False
    return True

def optional_input(text):
    """Allow yes or no input, returning True or False respectively"""
    while True:
        #Take input on whether to continue
        continuity_input = input(text)
        continuity_input_upper = continuity_input.upper() #Easier comparison

        if continuity_input_upper == "NO":
            return False
        elif continuity_input_upper == "YES":
            return True
        else:
            print("\n Please type either Yes or No, not case-sensitive")

def write_file(input_text,file_name):
    file = open(file_name, "w")
    file.write(input_text)
    file.close()

def append_to_file(input_text,file_name):
    file = open(file_name, "a")
    file.write(input_text)
    file.close()

main_standalone()
