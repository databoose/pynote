import os
import readline

from datetime import date
from datetime import datetime

def writing():
    msg = input("Enter your message (type exit to exit)\n\n>")
    if msg == "exit":
        quit()
    else:
        with open('journal.txt', 'a') as f:
            today = date.today()
            f.write("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n") # seperator
            f.write(today.strftime("%B %d, %Y") + " " + "@" + " " + datetime.today().strftime("%I:%M %p") + '\n\n')
            f.write(msg)
            f.write('\n')
            writing()


if __name__ == "__main__":
    print("----------------------------------")
    print("-PyNote, a python journal logger-")
    print("----------------------------------")
    if os.access("journal.txt", os.R_OK) is True:
        writing()

    elif os.access("journal.txt", os.R_OK) is False:
        print("journal.txt will be created in current directory as it does not exist.\n")
        answer = input("Is this okay? (Enter Y/N) : ")
        if answer == "Y":
            fp = open('journal.txt', 'w')
            print("journal file has been created\n")
            writing()
        elif answer == "N":
            quit()
