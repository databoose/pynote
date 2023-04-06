import os
import readline
import re

from datetime import date, datetime, timedelta
from time import strptime
from termcolor import colored, cprint

def getblocks():
    with open('journal.txt') as fp:
        lines = fp.read()
        fp.close()
        substring = '\n\n'
        res = len(re.findall(substring, lines)) # 2 \n\n's per block (or entry)
        return(int(res/2))

def readout():
    with open('journal.txt') as fp:
        print(colored("--- Start of File ---",'red'))
        while True:
            next_line = fp.readline() #grab new line
            recorded_date_string = ""
            recorded_time_string = ""

            timestamp_detected = False
            for pos_date, value_date in enumerate(next_line):
                if value_date == "(" and next_line.find("/") != -1 and next_line.find("@") != -1 and (next_line.find("PM") != -1 or next_line.find("AM") != -1):
                    timestamp_detected = True
                    while True:
                        pos_date += 1
                        value_date = next_line[pos_date]
                        if value_date == ")":
                            break;
                        recorded_date_string += value_date

            for pos_time, value in enumerate(next_line):
                if value == "@" and next_line.find("/") != -1 and (next_line.find("PM") != -1 or next_line.find("AM") != -1):
                    pos_time += 1 # 1 extra because we are skipping the space in between "@" and the time
                    while True:
                        pos_time += 1
                        value = next_line[pos_time]
                        if value == "\n": # break at end of line
                            break;
                        recorded_time_string += value
            if not next_line:
                break;
 
            if timestamp_detected == True:
                string_dt = recorded_date_string + " " + recorded_time_string
                object_dt = datetime.strptime(string_dt, '%m/%d/%Y %I:%M %p')
                
                current_time = datetime.now()
                time_delta = current_time - object_dt
                diff_days = time_delta.days
                diff_hours = time_delta.seconds // 3600

                print(next_line.strip(), end="") # print without newline so next print is on same line
                print(colored(" " + "[" + str(diff_days) + " " + "days and" + " " + str(diff_hours) + " " + "hours passed" + "]", 'green'))
            else:
                print(next_line.strip())
        fp.close()
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
            fp.write("(" + today.strftime(today.strftime("%m/%d/%Y")) + ")" + " " + "@" + " " + datetime.today().strftime("%I:%M %p") + '\n\n')
            fp.write(msg)
            fp.write('\n')
            print(colored('Entry written to journal','green'))
            fp.close()
            main()

def main():
    print("\n")
    cmd = input("Enter command (write, read, wipe, quit)\n\n>")
    if cmd == "read":
        readout()
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
            print(colored('Journal has been wiped','green'))
            main()
        if confirmation == "N":
            main()
    if cmd == "quit":
        quit()
    else:
        print(colored('Incorrect command.','red'))
        main()

if __name__ == "__main__":
    main()