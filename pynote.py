import os
import readline

from datetime import date

def writing():
    msg = input("Enter your message\n\n>")
    with open('journal.txt', 'w') as f:
        today = date.today()
        f.write(today.strftime("%B %d, %Y") + '\n')
        f.write(msg + '\n')


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
