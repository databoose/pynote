import os
import readline

from datetime import date, datetime, timedelta
from time import strptime
from termcolor import colored, cprint

# TODO: add CLI args, add note labels

def getblocks():
    block_size = 0
    with open('journal.txt') as fp:
        message = fp.readline()
        while message: # while current line has contents
            for current_char in message:
                if current_char == "(" and message.find("/") != -1 and message.find("@") != -1 and (message.find("PM") != -1 or message.find("AM") != -1):
                    block_size += 1
                    break;
            message = fp.readline()
    fp.close()
    return block_size

def parse_timestamp(message):
    recorded_date_string = ""
    recorded_time_string = ""
    timestamp_detected = False

    for pos_date, value_date in enumerate(message):
        if value_date == "(" and message.find("/") != -1 and message.find("@") != -1 and (message.find("PM") != -1 or message.find("AM") != -1):
            timestamp_detected = True
            while True: 
                pos_date += 1
                value_date = message[pos_date]
                if value_date == ")":
                    break
                recorded_date_string += value_date

    for pos_time, value in enumerate(message):
        if value == "@" and message.find("/") != -1 and (message.find("PM") != -1 or message.find("AM") != -1):
            pos_time += 1
            while True:
                pos_time += 1
                value = message[pos_time]
                if value == "\n":
                    break
                recorded_time_string += value

    if timestamp_detected:
        string_dt = recorded_date_string + " " + recorded_time_string
        object_dt = datetime.strptime(string_dt, '%m/%d/%Y %I:%M %p')
        current_time = datetime.now()
        time_delta = current_time - object_dt
        diff_days = time_delta.days
        diff_hours = time_delta.seconds // 3600
        return timestamp_detected, diff_days, diff_hours
    
    return timestamp_detected, None, None

def readout():
    with open('journal.txt') as fp:
        print(colored("--- Start of File ---",'red'))
        while True:
            message = fp.readline()
            if not message:
                break
            
            timestamp_detected, diff_days, diff_hours = parse_timestamp(message)
            
            print(message.strip(), end="")
            if timestamp_detected == True:
                print(colored(" " + "[" + str(diff_days) + " " + "days and" + " " + str(diff_hours) + " " + "hours passed" + "]", 'green'))
            else:
                print()
        fp.close()
        print(colored("--- End of File ---","red"))
        print(str(getblocks()) + " " + "entries")
        main()


def search():
    search_term = input("\nEnter search term:\n\n>")
    found = False
    with open('journal.txt') as fp:
        while True:
            timestamp_line = fp.readline()
            if not timestamp_line:
                break
                
            blank_line = fp.readline()
            message_line = fp.readline()
            
            if search_term in message_line:
                found = True

                timestamp_detected, diff_days, diff_hours = parse_timestamp(timestamp_line)
                if timestamp_detected:
                    print(colored(" " + "[" + str(diff_days) + " " + "days and" + " " + str(diff_hours) + " " + "hours passed" + "]", 'green'))
                else:
                    print()
                print(message_line.strip() + "\n")
            
            # Skip the next blank line after the message
            fp.readline()

    if not found:
        print(colored("\nNo matches found", 'red'))
    fp.close()
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
    if os.access("journal.txt", os.R_OK) is False:
        print("journal.txt will be created in current directory as it does not exist.\n")
        answer = input("Is this okay? (Enter Y/N) : ")
        if answer == "Y":
            fp = open('journal.txt', 'w')
            print(colored("Journal file has been created", 'green'))
            fp.close()
            main()
        elif answer == "N":
            quit()

    print("\n")
    cmd = input("Enter command (write, read, wipe, search, quit)\n\n>")
    match cmd:
        case "read":
            readout()
        case "write":
            writing()
        case "wipe":
            confirmation = input("Are you absolutely sure you want to wipe the journal? (Y\\N) \n\n>")
            if confirmation == "Y":
                open("journal.txt" , 'w').close()
                print(colored('Journal has been wiped','green'))
                main()
            if confirmation == "N":
                main()
        case "quit":
            quit()
        case "search":
            search()
        case _:
            print(colored('Incorrect command.','red'))
            main()
if __name__ == "__main__":
    main()
