from datetime import datetime, timezone, timedelta
from rich.console import Console
from rich.table import Table
from devlog.db import get_session
from devlog.models import Session

console = Console()


def list_sessions(today: bool, all_sessions: bool):
    db = get_session()

    query = db.query(Session).order_by(Session.start_time.desc())

    if today:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(Session.start_time >= start_of_day)
    elif not all_sessions:
        # Default: last 7 days
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        query = query.filter(Session.start_time >= week_ago)

    sessions = query.all()

    if not sessions:
        console.print("[dim]No sessions found.[/dim]")
        db.close()
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Description", min_width=25)
    table.add_column("Started", style="cyan")
    table.add_column("Duration", justify="right")
    table.add_column("Tags", style="green")

    for s in sessions:
        started = s.start_time.strftime("%b %d %H:%M")
        duration = f"{s.duration_minutes} min" if s.duration_minutes else "[yellow]active[/yellow]"
        tags = ", ".join(t.name for t in s.tags) or "—"
        table.add_row(str(s.id), s.description, started, duration, tags)

    console.print(table)
    db.close()
