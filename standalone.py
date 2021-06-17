import webbrowser
from source import programIO
from source import main
from source import filter_title

def main_standalone():
    if_continue = True
    while(if_continue):
        article_title = input("Enter the article title: ")
        
        if(if_title_valid(article_title)==True):
            html_output = main.main(filter_title.filter_title(article_title),if_ignore_URL_error=False)
            
            #Process backend output:
            if(html_output!="500"):
                programIO.write_file(html_output,"article.html")
                webbrowser.open("article.html")
            else:
                print("The article does not exist, or another error occurred.")
        else:
            print("Cancelling...")
        
        if_continue = optional_input("-------\n\nDo you wish to run the program again? Yes or No: ")

def if_title_valid(title):
    title_length = len(title)
    if(title_length>=256): #Article names must be less than 256 bytes
        print("An article cannot have this title (too long).")
        return False
    if(title_length==0): #Nothing entered
        print("No title entered.")
        return False
    if(filter_title.if_title_invalid_symbol_use(title)): #Problematic symbol use
        print("An article cannot have this title (invalid symbol use).")
        return False
    return True

#Yes or no input
def optional_input(text):
    while(True):
        #Take input on whether to continue
        continuity_input = input(text)
        continuity_input_upper = continuity_input.upper() #convert it to all uppercase to allow easy comparison
       
        if(continuity_input_upper == "NO"):
            return False
        elif(continuity_input_upper == "YES"):
            return True
        else:
            print("\n Please type either Yes or No, not case-sensitive")

main_standalone()