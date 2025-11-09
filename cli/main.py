import click
import requests
from datetime import datetime, timezone
import time
import subprocess
import sys

print("Executing cli/main.py")

SERVER_URL = "http://127.0.0.1:5000"

@click.group()
def cli():
    """A CLI tool to interact with the Qapi server."""
    pass

@cli.command()
def healthcheck():
    """Checks the health of the Qapi server."""
    try:
        response = requests.get(f"{SERVER_URL}/healthcheck")
        response.raise_for_status()
        click.echo(response.json())
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to the server: {e}")

@cli.command()
@click.argument('prompt')
def instruct(prompt):
    """Sends an instruction to the Qapi LLM."""
    try:
        response = requests.post(f"{SERVER_URL}/instruct", json={"prompt": prompt})
        response.raise_for_status()
        click.echo(response.json().get('response'))
    except requests.exceptions.RequestException as e:
        click.echo(f"Error communicating with the LLM: {e}")

@cli.command()
@click.argument('query')
def search(query):
    """Searches the data stores using a query."""
    try:
        response = requests.post(f"{SERVER_URL}/search", json={"query": query})
        response.raise_for_status()
        click.echo(response.json().get('response'))
    except requests.exceptions.RequestException as e:
        click.echo(f"Error searching: {e}")

@cli.command()
def create_timeheap():
    """Triggers the creation of the daily timeheap."""
    try:
        response = requests.post(f"{SERVER_URL}/create_daily_timeheap")
        response.raise_for_status()
        click.echo(response.json().get('response'))
    except requests.exceptions.RequestException as e:
        click.echo(f"Error creating timeheap: {e}")

@cli.command()
def setup_reminders():
    """Fetches the timeheap and sets up reminders."""
    click.echo("Fetching timeheap from server...")
    try:
        response = requests.get(f"{SERVER_URL}/timeheap")
        response.raise_for_status()
        timeheap = response.json()

        if "error" in timeheap:
            click.echo(f"Error fetching timeheap: {timeheap['error']}")
            return

        click.echo("Timeheap fetched successfully.")
        now = datetime.now(timezone.utc)
        
        for entry in timeheap:
            due_date_str = entry.get("due_date")
            if not due_date_str:
                click.echo(f"Skipping entry with no due_date: {entry}")
                continue

            try:
                due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                click.echo(f"Skipping entry with invalid due_date format: {entry}")
                continue

            # Ensure due_date is timezone-aware for comparison
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)

            if due_date > now:
                delay_seconds = (due_date - now).total_seconds()
                description = entry.get("description", "No description")
                
                # Get the absolute path to the Python executable
                python_executable = sys.executable
                
                # Get the absolute path to the reminder script
                reminder_script_path = "C:/Users/shrid/Desktop/Projects/Qapi/reminder/main.py"

                
                command = [
                    python_executable,
                    reminder_script_path,
                    f"--delay={delay_seconds}",
                    f"--message={description}"
                ]
                
                click.echo(f"Scheduling reminder for '{description}' in {delay_seconds} seconds.")
                subprocess.Popen(command)
        
        click.echo("Finished scheduling reminders.")

    except requests.exceptions.RequestException as e:
        click.echo(f"Error setting up reminders: {e}")


@cli.command()
def setup_reminders():
    """Fetches the timeheap and sets up reminders."""
    click.echo("Fetching timeheap from server...")
    try:
        response = requests.get(f"{SERVER_URL}/timeheap")
        response.raise_for_status()
        timeheap = response.json()

        if "error" in timeheap:
            click.echo(f"Error fetching timeheap: {timeheap['error']}")
            return

        click.echo("Timeheap fetched successfully.")
        
        # Use timezone-aware current time in UTC
        now = datetime.now(timezone.utc)
        click.echo(f"Current UTC time: {now.isoformat()}")
        
        scheduled_count = 0
        for entry in timeheap:
            due_date_str = entry.get("due_date")
            if not due_date_str:
                click.echo(f"Skipping entry with no due_date: {entry}")
                continue

            try:
                # Handle both 'Z' suffix and '+00:00' suffix for UTC
                due_date_str_cleaned = due_date_str.replace('Z', '+00:00')
                due_date = datetime.fromisoformat(due_date_str_cleaned)
                
                # Ensure timezone aware
                if due_date.tzinfo is None:
                    due_date = due_date.replace(tzinfo=timezone.utc)
                
                description = entry.get("description", "No description")
                click.echo(f"Task: '{description[:50]}...' Due: {due_date.isoformat()}")
                
            except ValueError as e:
                click.echo(f"Skipping entry with invalid due_date format: {due_date_str} - Error: {e}")
                continue

            if due_date > now:
                delay_seconds = (due_date - now).total_seconds()
                
                python_executable = sys.executable
                reminder_script_path = "C:/Users/shrid/Desktop/Projects/Qapi/reminder/main.py"

                command = [
                    python_executable,
                    reminder_script_path,
                    f"--delay={delay_seconds}",
                    f"--message={description}"
                ]
                
                click.echo(f"  -> Scheduling in {delay_seconds:.1f} seconds")
                subprocess.Popen(command)
                scheduled_count += 1
            else:
                time_diff = (now - due_date).total_seconds()
                click.echo(f"  -> PAST DUE by {time_diff:.0f} seconds, skipping")
        
        click.echo(f"\nFinished scheduling {scheduled_count} reminders.")

    except requests.exceptions.RequestException as e:
        click.echo(f"Error setting up reminders: {e}")

        
@cli.command()
def log():
    """Displays the contents of reminder.log."""
    try:
        with open("reminder.log", "r") as f:
            click.echo(f.read())
    except FileNotFoundError:
        click.echo("reminder.log not found.")

if __name__ == '__main__':
    cli()