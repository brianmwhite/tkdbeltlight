#!/usr/bin/env python3

from simple_term_menu import TerminalMenu
import os
import signal

SERVICE_NAME = "beltlight"

class exit_monitor_setup:
    exit_now_flag_raised = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.exit_now_flag_raised = True


if __name__ == "__main__":
    exit_monitor = exit_monitor_setup()

    while not exit_monitor.exit_now_flag_raised:
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