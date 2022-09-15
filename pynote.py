import os
import readline
import re

from datetime import date, datetime
from termcolor import colored, cprint

def getblocks():
    with open('journal.txt') as fp:
        lines = fp.read()
        substring = '\n\n'
        res = len(re.findall(substring, lines)) # 2 \n\n's per block (or entry)
        return(int(res/2))

def readout():
    with open('journal.txt') as fp:
        lines = fp.read()
        fp.close()
        print(colored("--- Start of File ---",'red'))
        cprint(lines, "white", "on_grey")
        print(colored("--- End of File ---","red"))
        print(str(getblocks()) + " " + "entries")
        main()

def writing():
    msg = input("\nEnter your message (type exit to exit)\n\n>")
    if msg == "exit":
        quit()
    else:
        with open('journal.txt', 'a') as fp: # open as appending
            today = date.today()
            fp.write("\n\n") # seperator
            fp.write("Entry #" + str(getblocks()+1) + "\n")
            fp.write(today.strftime("%B %d, %Y") + " " + "@" + " " + datetime.today().strftime("%I:%M %p") + '\n\n')
            fp.write(msg)
            fp.write('\n')
            print(colored('Entry written to journal','green'))
            fp.close()
            main()

def main():
    print("\n")
    cmd = input("Enter command (write, read, wipe, quit)\n\n>")
    if cmd == "write":
        if os.access("journal.txt", os.R_OK) is True:
            writing()
        
        elif os.access("journal.txt", os.R_OK) is False:
            print("journal.txt will be created in current directory as it does not exist.\n")
            answer = input("Is this okay? (Enter Y/N) : ")
            if answer == "Y":
                fp = open('journal.txt', 'w')
                print("journal file has been created\n")
                fp.close()
                main()
            elif answer == "N":
                quit()
    if cmd == "wipe":
        confirmation = input("Are you absolutely sure you want to wipe the journal? (Y\\N) \n\n>")
        if confirmation == "Y":
            open("journal.txt" , 'w').close()
            print("Journal has been wiped")
        if confirmation == "N":
            main()
    if cmd == "read":
        readout()
    if cmd == "quit":
        quit()

if __name__ == "__main__":
    main()
