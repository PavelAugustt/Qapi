import requests
import time
from plyer import notification
import json
import os
from datetime import datetime, timedelta

SERVER_URL = "http://127.0.0.1:5000"
REMINDER_INTERVAL_SECONDS = 300 # Check every 5 minutes
NOTIFICATION_TIMEOUT_SECONDS = 60 # Notification stays for 60 seconds

def get_timeheap():
    """Fetches the timeheap from the server."""
    try:
        response = requests.get(f"{SERVER_URL}/timeheap")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")
        return None

def show_reminder(task_description):
    """Displays a reminder notification."""
    notification.notify(
        title="Qapi Reminder: ACTION REQUIRED!",
        message=f"It's time for: {task_description}\n\n(This reminder will repeat until acknowledged)",
        app_name="Qapi",
        timeout=NOTIFICATION_TIMEOUT_SECONDS,
        toast=True # Attempt to make it a toast notification on Windows
    )
    print(f"Reminder: {task_description}")

def main():
    """Main loop for the reminder program."""
    # Corrected path to timeheap.json for initial setup
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    timeheap_path = os.path.join(data_dir, 'timeheap.json')

    # Placeholder: Ensure timeheap.json has a sample task for testing
    # In a real scenario, the server would manage this.
    if not os.path.exists(timeheap_path) or os.path.getsize(timeheap_path) == 0:
        with open(timeheap_path, "w") as f:
            # Set a due date in the near future for testing
            future_time = datetime.now() + timedelta(minutes=1)
            json.dump([{"description": "Complete the Qapi reminder system", "due_date": future_time.isoformat()}], f)

    last_reminded_task = None # To avoid spamming the same task immediately

    while True:
        current_time = datetime.now()
        timeheap = get_timeheap()

        if timeheap:
            # Sort timeheap by due_date to process the most urgent first
            timeheap.sort(key=lambda x: datetime.fromisoformat(x['due_date']))

            for task in timeheap:
                task_due_time = datetime.fromisoformat(task['due_date'])
                # Trigger reminder 5 minutes before or at the due time
                if current_time >= (task_due_time - timedelta(minutes=5)) and current_time <= task_due_time:
                    if last_reminded_task != task['description']: # Only show if it's a new task or not the immediate last one
                        show_reminder(task['description'])
                        last_reminded_task = task['description']
                    break # Only remind for the most urgent task at a time
        else:
            print("No timeheap data or error fetching it.")

        time.sleep(REMINDER_INTERVAL_SECONDS) # Check every 5 minutes