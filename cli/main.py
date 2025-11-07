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

if __name__ == '__main__':
    cli()