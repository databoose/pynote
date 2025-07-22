import os
import readline
import argparse
import math

from datetime import date, datetime, timedelta
from time import strptime
from termcolor import colored, cprint

# TODO : add active ncurses TUI interface?
#        make writing() check line spacings, maybe some auto-formatting?
#
def load_journal(file_path): # dump whole thing into ram to index, more costly on ram memory but the tradeoff is very fast performance
    try:
        with open(file_path, 'r') as file:
            lines = file.read().splitlines()
        return lines
    except FileNotFoundError:
        print(colored(f"Error: File not found at {file_path}", 'red'))
        return []
    except Exception as e:
        print(colored(f"An unexpected error occurred: {e}", 'red'))
        return []


def getblocks(journal_data):
    block_size = 0
    for message in journal_data:
        if (
            "(" in message
            and "/" in message
            and "@" in message
            and ("PM" in message or "AM" in message)
        ):
            block_size += 1
    return block_size


def parse_timestamp(message):
    timestamp_detected = False
    recorded_date_string = ""
    recorded_time_string = ""

    if (
        "(" in message
        and "/" in message
        and "@" in message
        and ("PM" in message or "AM" in message)
    ):
        timestamp_detected = True
        start_index = message.find("(") + 1
        end_index = message.find(")")
        recorded_date_string = message[start_index:end_index]

        start_time_index = message.find("@") + 1
        recorded_time_string = message[start_time_index:]

    if timestamp_detected:
        try:
            string_dt = recorded_date_string + " " + recorded_time_string.strip()
            object_dt = datetime.strptime(string_dt, "%m/%d/%Y %I:%M %p")
            current_time = datetime.now()
            time_delta = current_time - object_dt
            diff_days = time_delta.days
            diff_hours = time_delta.seconds // 3600
            return timestamp_detected, diff_days, diff_hours
        except ValueError:
            print(colored(f"Invalid timestamp format: {string_dt}", "yellow"))
            return False, None, None
    return timestamp_detected, None, None


def readout(journal_data):
    print(colored("--- Start of File ---", "red"))
    for message in journal_data:
        timestamp_detected, diff_days, diff_hours = parse_timestamp(message)

        print(message.strip(), end="")
        if timestamp_detected:
            weeks = math.trunc(diff_days / 7 * 10) / 10
            months = math.trunc(diff_days / 30 * 10) / 10
            print(colored(f" [{diff_days} days and {diff_hours} hours passed] ({weeks:.1f} weeks and {months:.1f} months)", "green"))
        else:
            print()
    print(colored("--- End of File ---", "red"))
    print(str(getblocks(journal_data)) + " " + "entries")


def search(journal_data, search_term):
    found = False
    for message in journal_data:
        if search_term in message:
            found = True
            timestamp_detected, diff_days, diff_hours = parse_timestamp(message)
            print(message.strip())
            if timestamp_detected:
                print(colored(" " + "[" + str(diff_days) + " " + "days and" + " " + str(diff_hours) + " " + "hours passed" + "]", "green",))
            else:
                print()

    if not found:
        print(colored("No matches found", "red"))


def writing(message=None):
    if message is None:
        msg = input("\nEnter your message (type exit to exit)\n\n>")
        if msg == "exit":
            quit()
    else:
        msg = message
    try:
        with open("journal.txt", "a") as fp:
            today = date.today()
            timestamp = "(" + today.strftime("%m/%d/%Y") + ")" + " " + "@" + " " + datetime.now().strftime("%I:%M %p") + "\n\n"
            fp.write(timestamp)
            fp.write(msg + "\n\n")
        print(colored("Entry written to journal", "green"))
    except Exception as e:
        print(colored(f"Error writing to journal: {e}", "red"))


def wipe_journal(interactive=True):
    if interactive:
        confirmation = input("Are you absolutely sure you want to wipe the journal? (Y/N) \n\n>")
        if confirmation.upper() == "Y":
            try:
                with open("journal.txt", "w") as fp:
                    fp.truncate(0)
                print(colored("Journal has been wiped", "green"))
            except Exception as e:
                print(colored(f"Error wiping journal: {e}", "red"))
        elif confirmation.upper() == "N":
            return
        else:
            print(colored("Invalid input. Journal not wiped.", "yellow"))
    else:
        try:
            with open("journal.txt", "w") as fp:
                fp.truncate(0)
            print(colored("Journal has been wiped", "green"))
        except Exception as e:
            print(colored(f"Error wiping journal: {e}", "red"))


def main():
    parser = argparse.ArgumentParser(description="Journal management CLI")
    parser.add_argument(
        "--read",
        action="store_true",
        help="Read the journal entries",
    )
    parser.add_argument(
        "--write",
        type=str,
        metavar="MESSAGE",
        help="Write a new entry to the journal",
    )
    parser.add_argument(
        "--wipe",
        action="store_true",
        help="Wipe the journal (non-interactive)",
    )
    parser.add_argument(
        "--search",
        type=str,
        metavar="TERM",
        help="Search for a term in the journal",
    )
    args = parser.parse_args()
    if not os.path.exists("journal.txt"):
        print("journal.txt will be created in the current directory as it does not exist.\n")
        answer = input("Is this okay? (Y/N) : ")
        if answer.upper() == "Y":
            try:
                with open("journal.txt", "w") as fp:
                    print(colored("Journal file has been created", "green"))
            except Exception as e:
                print(colored(f"Error creating journal: {e}", "red"))
                return
        elif answer.upper() == "N":
            quit()
        else:
            print(colored("Invalid input. Exiting.", "yellow"))
            return

    journal_data = load_journal("journal.txt")
    if not journal_data and not (args.write or args.wipe):
        return

    # cli args
    if args.read:
        readout(journal_data)
        return
    elif args.write:
        writing(args.write)
        return
    elif args.wipe:
        wipe_journal(interactive=False)
        return
    elif args.search:
        search(journal_data, args.search)
        return

    # default interactive mode when user doesn't provide cli args
    while True:
        print("\n")
        cmd = input("Enter command (write, read, wipe, search, quit)\n\n>")
        match cmd:
            case "read":
                readout(journal_data)
            case "write":
                writing()
                journal_data = load_journal("journal.txt")
            case "wipe":
                wipe_journal()
                journal_data = load_journal("journal.txt")
            case "search":
                search_query = input("Enter string to search for : ")
                search(journal_data, search_query)
            case "quit":
                break
            case _:
                print(colored("Incorrect command.", "red"))

if __name__ == "__main__":
    main()
