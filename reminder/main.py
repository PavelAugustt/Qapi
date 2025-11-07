import requests
import time
from plyer import notification

SERVER_URL = "http://127.0.0.1:5000"

def get_timeheap():
    """Fetches the timeheap from the server."""
    try:
        response = requests.get(f"{SERVER_URL}/timeheap")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")
        return None

def show_reminder(task):
    """Displays a reminder notification."""
    notification.notify(
        title="Qapi Reminder",
        message=f"It's time for: {task['description']}",
        app_name="Qapi",
    )
    print(f"Reminder: {task['description']}")

def main():
    """Main loop for the reminder program."""
    while True:
        timeheap = get_timeheap()
        if timeheap:
            print("Current timeheap:", timeheap)
            # In a real implementation, you would check the timestamps
            # and trigger reminders at the appropriate time.
            # For now, we'll just show a reminder for the first task.
            if timeheap:
                show_reminder(timeheap[0])

        # Check for new tasks every hour
        time.sleep(3600)


if __name__ == '__main__':
    # As a placeholder, let's add a sample task to the timeheap.json
    # In a real scenario, the server would manage this.
    import json
    with open("../data/timeheap.json", "w") as f:
        json.dump([{"description": "This is a test task", "due_date": "2025-11-06T21:00:00"}], f)
    main()