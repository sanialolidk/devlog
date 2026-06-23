import click
from devlog.commands.start import start_session
from devlog.commands.stop import stop_session
from devlog.commands.tag import tag_session
from devlog.commands.list_sessions import list_sessions


@click.group()
@click.version_option(package_name="devlog")
def cli():
    """DevLog — track your dev sessions from the terminal."""
    pass


@cli.command()
@click.argument("description")
def start(description):
    """Start a new work session."""
    start_session(description)


@cli.command()
def stop():
    """Stop the current active session."""
    stop_session()


@cli.command()
@click.argument("tags", nargs=-1, required=True)
def tag(tags):
    """Tag the most recent session with one or more tags."""
    tag_session(tags)


@cli.command("list")
@click.option("--today", is_flag=True, help="Show only today's sessions")
@click.option("--all", "all_sessions", is_flag=True, help="Show all sessions")
def list_cmd(today, all_sessions):
    """List sessions (default: last 7 days)."""
    list_sessions(today, all_sessions)
