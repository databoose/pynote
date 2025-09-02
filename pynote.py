import os
import sys
import argparse
import sqlite3
import re

from datetime import datetime
from termcolor import colored
from typing import List, Dict, Optional

# todo
# add journal "sections" functionality
# make search function return properly formatted entry when searching by ID

class JournalManager():
    def __init__(self, db_path: str):
        self.db_path = db_path

    def init_database(self) -> None:
        with sqlite3.connect(self.db_path) as db:
            try:
                db.execute("""
                    CREATE TABLE IF NOT EXISTS entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        timestamp DATETIME NOT NULL
                    )
                """)
            except Exception as e:
                 print(colored(f"sqlite error occured, unable to create database : {e}", "red"))
                 sys.exit()

    def calculate_time_diff(self, timestamp: datetime) -> tuple[int, int]:
        if not isinstance(timestamp, datetime):
            print(colored("Error in calculate_time_diff", "red"))
            raise TypeError(f"Expected datetime, got {type(timestamp).__name__}")
        now = datetime.now()
        delta = now - timestamp
        days = delta.days
        hours = (delta.seconds // 3600)
        return days, hours

    def load_journal(self) -> List[Dict[str, any]]: # keys are strings, values can be any type
        try:
            with sqlite3.connect(self.db_path) as db:
                rows = db.execute("SELECT id, content, timestamp FROM entries ORDER BY timestamp ASC").fetchall()
                return [{"id": row[0], "content": row[1], "timestamp": datetime.fromisoformat(row[2])} for row in rows]
        except Exception as e:
            print(colored(f"sqlite error occured, unable to load journal : {e}", e))
            sys.exit()
    
    # we wont need this later
    def get_entry_count(self) -> int:
        try:
            with sqlite3.connect(self.db_path) as db:
                row = db.execute("SELECT COUNT(*) as count FROM entries").fetchone()
                return row[0] if row else 0
        except Exception as e:
            print(colored(f"sqlite error occured, unable to get entry count : {e}", "red"))
            return 0

    def readout(self) -> None:
        try:
            entries = self.load_journal()
            print(colored("--- Start of Journal ---", "red"))

            for i, entry in enumerate(entries):
                days_passed, hours_passed = self.calculate_time_diff(entry["timestamp"])

                weeks_passed = f"{(days_passed / 7):.1f}"
                months_passed = f"{(days_passed / 30):.1f}"
                timestamp_display = f"({entry['timestamp'].strftime('%m/%d/%Y')}) @ {entry['timestamp'].strftime('%I:%M %p')}"
                time_passed = f"[{days_passed} days and {hours_passed} hours passed] ({weeks_passed} weeks and {months_passed} months)"

                print(colored(f"[Entry ID : {entry["id"]}]", "blue"))
                print(timestamp_display + " " + colored(time_passed, "green"))

                print()
                print(entry["content"])

                if i < len(entries) - 1: # spacing between each entry
                    print()

            print()
            print(colored("--- End of Journal ---", "red"))
            print(f"{self.get_entry_count()} entries")
        except Exception as e:
            print(colored(f"Error loading database: {e}", "red"))

    # TODO make this look cleaner for the user, output is kinda messy
    def search(self, substr=None, row_id=None) -> None:
        try:
            entries = self.load_journal()
            found = False

            if substr:
                for entry in entries:
                    if substr.lower() in entry["content"].lower():
                        found = True
                        days_passed, hours_passed = self.calculate_time_diff(entry["timestamp"])

                        weeks_passed = f"{(days_passed / 7):.1f}"
                        months_passed = f"{(days_passed / 30):.1f}"
                        timestamp_display = f"({entry['timestamp'].strftime('%m/%d/%Y')}) @ {entry['timestamp'].strftime('%I:%M %p')}"
                        time_passed = f"[{days_passed} days and {hours_passed} hours passed] ({weeks_passed} weeks and {months_passed} months)"

                        print(colored(f"[Entry ID : {entry["id"]}]", "blue"))
                        print(colored(timestamp_display, "white"))
                        print(colored(time_passed, "green"))
                        print()
                        print(entry["content"])
                        print()
            if row_id:
                with sqlite3.connect(self.db_path) as db:
                    cursor = db.cursor()
                    row_content = cursor.execute("SELECT content FROM entries WHERE id = ?", (row_id,)).fetchone()

                    if row_content:
                        found = True
                        print(f"Text of entry ID [{row_id}] : \n\n", row_content[0])
                    else:
                        found = False
                        print(f"No row found with ID {row_id}")
            if not found:
                print(colored("No matches found", "red"))
        except Exception as e:
            print(colored(f"Error searching journal: {e}", "red"))

    def get_multiline_input(self) -> Optional[str]:
        print("\nEnter your message (press Ctrl+C to cancel or type '###END###' on a new line to finish)")
        print("Use empty lines to separate paragraphs\n")

        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "###END###":
                    break
                lines.append(line)
        except KeyboardInterrupt:
            print(colored("\nEntry cancelled", "yellow"))
            return None
        except EOFError:
            return None

        return "\n".join(lines) if lines else None

    def write_entry(self, message: Optional[str] = None) -> None:
        msg = message
        if msg is None:
            choice = input("\nChoose input method:\n1. Single line\n2. Multi-line\nEnter choice (1/2, default: 1): ").strip()
            if choice == "2":
                msg = self.get_multiline_input()
                if msg is None:
                    return
            else:
                msg = input("\nEnter your message (type exit to exit)\n\n>")
                if msg.strip() == "exit":
                    return

        try:
            with sqlite3.connect(self.db_path) as db:
                db.execute(
                    "INSERT INTO entries (content, timestamp) VALUES (?, ?)",
                    (msg, datetime.now().isoformat())
                )
            print(colored("Entry written to journal", "green"))
        except Exception as e:
            print(colored(f"Error writing to journal: {e}", "red"))

    def wipe_journal(self, interactive: bool = True) -> None:
        if interactive:
            confirmation = input("Are you absolutely sure you want to wipe the journal? (Y/N) \n\n>").strip().upper()
            if confirmation != "Y":
                if confirmation != "N":
                    print(colored("Invalid input. Journal not wiped.", "yellow"))
                return

        try:
            with sqlite3.connect(self.db_path) as db:
                db.execute("DELETE FROM entries")
            print(colored("Journal has been wiped", "green"))
        except Exception as e:
            print(colored(f"Error wiping journal: {e}", "red"))
    
    def delete_entry(self, row_id: int):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            try:
                cursor.execute('SELECT 1 FROM entries WHERE id = ?', (row_id,))
                exists = cursor.fetchone()
                if exists:
                    cursor.execute('''
                                    DELETE FROM entries
                                    WHERE id = ? ''' , (row_id,))
                    print(colored(f"Entry {row_id} deleted", "green"))
                    print(cursor.fetchall())
                else:
                    print(colored("Entry with that ID does not exist.", "red"))
            except Exception as e:
                print(colored(f"sqlite error occured, delete operation failed : {e}", "red"))

    def replace_entry(self, row_id: int):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            try:
                cursor.execute('''
                            SELECT * FROM
                            entries
                            WHERE id = ? ''', (row_id,))
            except Exception as e:
                print(colored(f"sqlite error occured : {e}", "red"))

            row_text = cursor.fetchone() # returns a tuple containing row id, content, and timestamp
            if not row_text:
                print(colored(f"No row found for ID {row_id}"))
                return None
            else:
                lines = []
                print("The original text for this entry : \n\n")
                print(row_text[1])
                print("\n Enter in new text (press Ctrl+C to cancel or type '###END###' on a new line to finish\n")
                try:
                    while True:
                        line = input()
                        if line.strip() == "###END###":
                            break
                        lines.append(line)
                except KeyboardInterrupt:
                    print(colored("\nEntry cancelled", "yellow"))
                    return None
                except EOFError:
                    print(colored("EOF error in edit_entry(), this should not happen","red"))

                msg = "\n".join(lines)
                try:
                    cursor.execute('''
                            UPDATE entries
                            SET content = ?
                            WHERE id = ? ''' , (msg, row_id))
                except Exception as e:
                    print(colored(f"sqlite error occured : {e}", "red"))

    # @staticmethod defines a method that belongs to the class rather than to an instance of this class
    @staticmethod
    def convert_text_journal_to_db(input_file: str = "journal.txt", output_db: str = "journal.db"):
        try:
            with open(input_file, "r") as f:
                journal_text = f.read()

            pattern = r"\((\d{2}/\d{2}/\d{4})\) @ (\d{1,2}:\d{2} [AP]M)\s*\n\s*\n(.*?)(?=\(\d{2}/\d{2}/\d{4}\)|$)"
            matches = re.finditer(pattern, journal_text, re.DOTALL)
            entries = []

            for match in matches:
                date_str, time_str, content = match.groups()
                date_time_str = f"{date_str} {time_str}"
                dt = datetime.strptime(date_time_str, "%m/%d/%Y %I:%M %p")
                if dt:
                    entries.append({
                        "timestamp": dt,
                        "content": content.strip()
                    })

            if not entries:
                return False

            conn = sqlite3.connect(output_db)
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        timestamp DATETIME NOT NULL
                    )
                """)

                for entry in entries:
                    conn.execute(
                        "INSERT INTO entries (content, timestamp) VALUES (?, ?)",
                        (entry["content"], entry["timestamp"].isoformat())
                    )
        except Exception as e:
            print(colored(f"Error during migration: {e}", "red"))
            sys.exit()

def ask_question(question: str) -> str:
    return input(question).strip()

def print_help():
    print ("\nCommands : \n")
    print("  read (prints journal)")
    print("  write (writes entry to journal)")
    print("  replace (replaces a specific entry with new text)")
    print("  wipe (wipes journal)")
    print("  search (searches for term in journal)")
    print("  delete (deletes an entry)")
    print("  help (prints this message)")
    print("  quit (quits program) ")
    print("\n")

def main():
    db_path = "journal.db"
    if not os.path.exists(db_path):
        if os.path.exists("journal.txt"):
            cmd = ask_question("journal.txt file found, txt-based journals are legacy, do you want to migrate your journal? (Y or N) ")
            if cmd.upper() == "Y":
                JournalManager.convert_text_journal_to_db()

    if not os.path.exists(db_path):
        print(f"{db_path} will be created in the current directory as it does not exist.\n")
        answer = ask_question("Is this okay? (Y/N) : ")
        if answer.upper() == "Y":
            journal_temp = JournalManager(db_path)
            journal_temp.init_database()
            print(colored("Journal database has been created", "green"))
        elif answer.upper() == "N":
            return
        else:
            print(colored("Invalid input. Exiting.", "yellow"))
            return

    journal = JournalManager(db_path)

    parser = argparse.ArgumentParser(description="Journal management CLI")
    parser.add_argument("--read", action="store_true", help="Read the journal entries")
    parser.add_argument("--write", type=str, nargs="?", const=None, help="Write a new entry to the journal")
    parser.add_argument("--wipe", action="store_true", help="Wipe the journal (non-interactive)")
    parser.add_argument("--search", type=str, help="Search for a term in the journal")
    args = parser.parse_args()

    if args.read:
        journal.readout()
        return
    elif args.write is not None:
        journal.write_entry(args.write)
        return
    elif args.wipe:
        journal.wipe_journal(interactive=False)
        return
    elif args.search:
        journal.search(args.search)
        return

    print(colored("\nJournal CLI - Using database", "blue"))
    print_help()

    while True:
        cmd = input("\nEnter command (read, write, delete, replace, wipe, search, help, quit)\n\n>").strip()
        if cmd == "read":
            journal.readout()
        elif cmd == "write":
            journal.write_entry()
        elif cmd == "replace":
            entry_num = ask_question("Enter entry number to edit: ").strip()
            try:
                entry_num = int(entry_num)
                if entry_num < 1:
                    print(colored("Invalid input, entry number must be a positive number"), "red")
                else:
                    journal.replace_entry(entry_num)
            except ValueError:
                print(colored("Invalid input, enter a number."))
            except Exception as e:
                print(f"Exception type: {type(e).__name__}")
                print(colored(e,"red"))
        elif cmd == "wipe":
            journal.wipe_journal()
        elif cmd == "search":
            ans = ask_question("Search by entry ID or text? ('string' or 'id'): ")
            if ans == "string":
                search_query = ask_question("Enter string to search for: ")
                journal.search(search_query)
            elif ans == "id":
                id = int(ask_question("Enter entry ID : "))
                journal.search(None, id)
            else:
                print(colored("Incorrect input"), "red")
        elif cmd == "delete":
            ans = ask_question("Enter entry ID to delete : ")
            try:
                journal.delete_entry(int(ans))
            except ValueError as ve:
                print(colored(f"Incorrect type : {ve}"), "red")
        elif cmd == "help":
            print_help()
        elif cmd == "quit":
            break
        else:
            print(colored("Incorrect command.", "red"))

if __name__ == "__main__":
    main()