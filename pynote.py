import os
import readline

from datetime import date, datetime, timedelta
from time import strptime
from termcolor import colored, cprint

'''
TODO: 
    - add search and delete functions
'''

def getblocks():
    block_size = 0
    with open('journal.txt') as fp:
        current_line = fp.readline()
        while current_line: # while current line has contents
            for current_char in current_line:
                if current_char == "(" and current_line.find("/") != -1 and current_line.find("@") != -1 and (current_line.find("PM") != -1 or current_line.find("AM") != -1):
                    block_size += 1
                    break;
            current_line = fp.readline()
    fp.close()
    return block_size

def readout():
    with open('journal.txt') as fp:
        print(colored("--- Start of File ---",'red'))
        while True:
            current_line = fp.readline() #grab new line
            recorded_date_string = ""
            recorded_time_string = ""

            timestamp_detected = False
            for pos_date, value_date in enumerate(current_line):
                if value_date == "(" and current_line.find("/") != -1 and current_line.find("@") != -1 and (current_line.find("PM") != -1 or current_line.find("AM") != -1):
                    timestamp_detected = True
                    while True: 
                        pos_date += 1
                        value_date = current_line[pos_date]
                        if value_date == ")":
                            break;
                        recorded_date_string += value_date

            for pos_time, value in enumerate(current_line):
                if value == "@" and current_line.find("/") != -1 and (current_line.find("PM") != -1 or current_line.find("AM") != -1):
                    pos_time += 1 # 1 extra because we are skipping the space in between "@" and the time
                    while True:
                        pos_time += 1
                        value = current_line[pos_time]
                        if value == "\n": # break at end of line
                            break;
                        recorded_time_string += value
            if not current_line: #if current line does not have contents, aka when we are done reading the entire file then break out of while loop
                break;
 
            if timestamp_detected == True:
                string_dt = recorded_date_string + " " + recorded_time_string
                object_dt = datetime.strptime(string_dt, '%m/%d/%Y %I:%M %p')
                
                current_time = datetime.now()
                time_delta = current_time - object_dt
                diff_days = time_delta.days
                diff_hours = time_delta.seconds // 3600

                print(current_line.strip(), end="") # print without newline so next print is on same line
                print(colored(" " + "[" + str(diff_days) + " " + "days and" + " " + str(diff_hours) + " " + "hours passed" + "]", 'green'))
            else:
                print(current_line.strip())
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