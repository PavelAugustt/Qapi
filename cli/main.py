import click
import requests

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

if __name__ == '__main__':
    cli()