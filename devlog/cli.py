import click
from devlog.commands.start import start_session
from devlog.commands.stop import stop_session
from devlog.commands.tag import tag_session
from devlog.commands.list_sessions import list_sessions
from devlog.commands.report import report_sessions
from devlog.commands.resume import resume_session
from devlog.commands.export import export_sessions
from devlog.commands.summary import ai_summary


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


@cli.command()
@click.option("--today", "period", flag_value="today", help="Report for today")
@click.option("--week", "period", flag_value="week", default=True,
              help="Report for last 7 days (default)")
def report(period):
    """Show a summary report of your sessions."""
    report_sessions(period)


@cli.command()
@click.argument("session_id", type=int)
def resume(session_id):
    """Restart a past session by creating a new one with the same description."""
    resume_session(session_id)


@cli.command("export")
@click.option("--format", "fmt", type=click.Choice(["csv", "json"]),
              default="csv", show_default=True)
@click.option("--today", "period", flag_value="today", help="Export only today's sessions")
@click.option("--week", "period", flag_value="week", help="Export last 7 days")
@click.option("--all", "period", flag_value="all", default=True,
              help="Export all sessions (default)")
@click.option("--output", "-o", default=None, help="Output file path (default: stdout)")
def export_cmd(fmt, period, output):
    """Export sessions to CSV or JSON."""
    export_sessions(fmt, period, output)


@cli.command()
@click.option("--today", "period", flag_value="today", help="Summarize today's sessions")
@click.option("--week", "period", flag_value="week", default=True,
              help="Summarize last 7 days (default)")
def summary(period):
    """Use AI to recap what you worked on."""
    ai_summary(period)
