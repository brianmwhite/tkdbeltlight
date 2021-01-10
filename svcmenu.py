#!/usr/bin/env python3

from simple_term_menu import TerminalMenu
import os

SERVICE_NAME = "beltlight"

def main():
    print("beltlight service commands...")
    
    terminal_menu = TerminalMenu(["stop", "restart", "logs", "start", "status"])
    menu_entry_index = terminal_menu.show()

    if menu_entry_index == 0:
        os.system(f"sudo systemctl stop {SERVICE_NAME}")
    elif menu_entry_index == 1:
        os.system(f"sudo systemctl restart {SERVICE_NAME}")
    elif menu_entry_index == 2:
        os.system(f"journalctl -u {SERVICE_NAME} -f")
    elif menu_entry_index == 3:
        os.system(f"sudo systemctl start {SERVICE_NAME}")
    elif menu_entry_index == 4:
        os.system(f"systemctl status {SERVICE_NAME}")

if __name__ == "__main__":
    main()