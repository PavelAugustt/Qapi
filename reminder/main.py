import time
from plyer import notification
import argparse
import logging
import os

# Construct the absolute path for the log file
log_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file_path = os.path.join(log_dir, 'reminder.log')

logging.basicConfig(filename=log_file_path, level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def show_reminder(task_description):
    """Displays a reminder notification."""
    logging.info(f"Showing reminder for: {task_description}")
    notification.notify(
        title="Qapi Reminder: ACTION REQUIRED!",
        message=f"It's time for: {task_description}",
        app_name="Qapi",
        timeout=60, # Notification stays for 60 seconds
        toast=True # Attempt to make it a toast notification on Windows
    )
    logging.info(f"Finished showing reminder for: {task_description}")

def main():
    """Main function for the reminder script."""
    parser = argparse.ArgumentParser(description="Qapi Reminder")
    parser.add_argument("--delay", type=float, required=True, help="Delay in seconds before showing the reminder.")
    parser.add_argument("--message", type=str, required=True, help="The reminder message.")
    args = parser.parse_args()

    logging.info(f"Reminder scheduled for '{args.message}' in {args.delay} seconds.")
    time.sleep(args.delay)
    show_reminder(args.message)

if __name__ == "__main__":
    main()