from datetime import datetime, timezone
import click
from rich.console import Console
from devlog.db import get_session
from devlog.models import Session

console = Console()


def stop_session():
    db = get_session()

    active = db.query(Session).filter(Session.end_time.is_(None)).first()
    if not active:
        console.print("[yellow]No active session.[/yellow] Run [bold]devlog start[/bold] first.")
        db.close()
        return

    active.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(active)

    duration = active.duration_minutes
    console.print(f"[green]Stopped:[/green] {active.description}")
    console.print(f"[dim]Duration: {duration} min[/dim]")
    db.close()
