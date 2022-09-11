import os
import readline

from datetime import date, datetime

def writing():
    msg = input("Enter your message (type exit to exit)\n\n>")
    if msg == "exit":
        quit()
    else:
        with open('journal.txt', 'a') as f: # open as appending
            today = date.today()
            f.write("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n") # seperator
            f.write(today.strftime("%B %d, %Y") + " " + "@" + " " + datetime.today().strftime("%I:%M %p") + '\n\n')
            f.write(msg)
            f.write('\n')
            f.close()
            main()

def main():
    print("----------------------------------")
    print("-PyNote, a python journal logger-")
    print("----------------------------------")
    cmd = input("Enter command (write, wipe, quit) \n\n>")
    if cmd == "write":
        if os.access("journal.txt", os.R_OK) is True:
            writing()
        
        elif os.access("journal.txt", os.R_OK) is False:
            print("journal.txt will be created in current directory as it does not exist.\n")
            answer = input("Is this okay? (Enter Y/N) : ")
            if answer == "Y":
                fp = open('journal.txt', 'w')
                print("journal file has been created\n")
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
    if cmd == "quit":
        quit()

if __name__ == "__main__":
    main()