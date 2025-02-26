import argparse
import sys
import signal

try:
    import gnureadline  
except ImportError: 
    import pyreadline
    is_windows = True
else:
    is_windows = False

from src import printcolors as pc
from src import artwork
import Osintgram


def print_logo():
    """Prints the ASCII logo and usage instructions."""
    pc.printout(artwork.ascii_art, pc.YELLOW)
    pc.printout("\nVersion 1.1 - Developed by Giuseppe Criscione\n\n", pc.YELLOW)
    instructions = [
        "Type 'list' to show all allowed commands",
        "Type 'FILE=y' to save results to files (default is disabled)",
        "Type 'FILE=n' to disable saving to files",
        "Type 'JSON=y' to export results as JSON files (default is disabled)",
        "Type 'JSON=n' to disable exporting to files"
    ]
    for line in instructions:
        pc.printout(line + "\n")


def print_commands():
    """Prints the available commands for the tool."""
    command_list = {
        "FILE=y/n": "Enable/disable output in '<target username>_<command>.txt'",
        "JSON=y/n": "Enable/disable export in '<target username>_<command>.json'",
        "addrs": "Get all registered addresses from target's photos",
        "cache": "Clear cache of the tool",
        "captions": "Get target's photo captions",
        "commentdata": "Get a list of all comments on target's posts",
        "comments": "Get total comments on target's posts",
        "followers": "Get target's followers",
        "followings": "Get users followed by target",
        "fwersemail": "Get FULL email addresses of target's followers",
        "fwingsemail": "Get FULL email addresses of users followed by target",
        "fwersnumber": "Get FULL phone numbers of target's followers",
        "fwingsnumber": "Get FULL phone numbers of users followed by target",
        "hashtags": "Get hashtags used by target",
        "info": "Get target info",
        "likes": "Get total likes on target's posts",
        "mediatype": "Get types of target's posts (photo/video)",
        "photodes": "Get descriptions of target's photos",
        "photos": "Download target's photos",
        "propic": "Download target's profile picture",
        "stories": "Download target's stories",
        "tagged": "Get users tagged by target",
        "target": "Set a new target",
        "wcommented": "Get users who commented on target's photos",
        "wtagged": "Get users who tagged the target",
    }
    for cmd, desc in command_list.items():
        pc.printout(f"{cmd}\t\t")
        print(desc)


def signal_handler(sig, frame):
    """Handles Ctrl+C (SIGINT) to exit gracefully."""
    pc.printout("\nGoodbye!\n", pc.RED)
    sys.exit(0)


def setup_autocomplete():
    """Configures command autocompletion based on the OS."""
    if is_windows:
        readline = pyreadline.Readline()
    else:
        readline = gnureadline
    readline.parse_and_bind("tab: complete")
    readline.set_completer(lambda text, state: [cmd for cmd in commands.keys() if cmd.startswith(text)][state] if state < len(commands) else None)


def main():
    """Main function to parse arguments and start the CLI tool."""
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Osintgram: OSINT tool for Instagram analysis.")
    parser.add_argument("id", type=str, help="Instagram username")
    parser.add_argument("-C", "--cookies", help="Clear previous cookies", action="store_true")
    parser.add_argument("-j", "--json", help="Save command output as JSON", action="store_true")
    parser.add_argument("-f", "--file", help="Save output in a file", action="store_true")
    parser.add_argument("-c", "--command", help="Run a single command and exit", action="store")
    parser.add_argument("-o", "--output", help="Specify output directory", action="store")

    args = parser.parse_args()

    # Validate username (basic check)
    if not args.id.isalnum():
        pc.printout("Invalid Instagram username. It should be alphanumeric.\n", pc.RED)
        sys.exit(1)

    # Initialize API
    api = Osintgram(args.id, args.file, args.json, args.command, args.output, args.cookies)

    # Define command functions
    commands = {
        "list": print_commands,
        "help": print_commands,
        "quit": sys.exit,
        "exit": sys.exit,
        "addrs": api.get_addrs,
        "cache": api.clear_cache,
        "captions": api.get_captions,
        "commentdata": api.get_comment_data,
        "comments": api.get_total_comments,
        "followers": api.get_followers,
        "followings": api.get_followings,
        "fwersemail": lambda: print_full_data(api.get_fwersemail(), "Follower Emails"),
        "fwingsemail": lambda: print_full_data(api.get_fwingsemail(), "Following Emails"),
        "fwersnumber": lambda: print_full_data(api.get_fwersnumber(), "Follower Phone Numbers"),
        "fwingsnumber": lambda: print_full_data(api.get_fwingsnumber(), "Following Phone Numbers"),
        "hashtags": api.get_hashtags,
        "info": api.get_user_info,
        "likes": api.get_total_likes,
        "mediatype": api.get_media_type,
        "photodes": api.get_photo_description,
        "photos": api.get_user_photo,
        "propic": api.get_user_propic,
        "stories": api.get_user_stories,
        "tagged": api.get_people_tagged_by_user,
        "target": api.change_target,
        "wcommented": api.get_people_who_commented,
        "wtagged": api.get_people_who_tagged,
    }

    if args.command:
        cmd_function = commands.get(args.command)
        if cmd_function:
            cmd_function()
        else:
            pc.printout(f"Unknown command: {args.command}\n", pc.RED)
        return

    print_logo()

    while True:
        try:
            pc.printout("Run a command: ", pc.YELLOW)
            cmd = input().strip()
            if not cmd:
                continue
            elif cmd in commands:
                commands[cmd]()
            elif cmd == "FILE=y":
                api.set_write_file(True)
            elif cmd == "FILE=n":
                api.set_write_file(False)
            elif cmd == "JSON=y":
                api.set_json_dump(True)
            elif cmd == "JSON=n":
                api.set_json_dump(False)
            else:
                pc.printout("Unknown command\n", pc.RED)
        except Exception as e:
            pc.printout(f"Error: {e}\n", pc.RED)


def print_full_data(data, title):
    """Formats and prints full email addresses and phone numbers."""
    pc.printout(f"\n[+] {title}:\n", pc.GREEN)
    if not data:
        pc.printout("[-] No data found.\n", pc.RED)
        return
    for item in data:
        pc.printout(f"  - {item}\n", pc.CYAN)


if __name__ == "__main__":
    main()
