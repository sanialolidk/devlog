from datetime import datetime, timezone
import click
from rich.console import Console
from devlog.db import get_session
from devlog.models import Session

console = Console()


def stop_session():
    db = get_session()
    try:
        active = db.query(Session).filter(Session.end_time.is_(None)).first()
        if not active:
            console.print("[yellow]No active session.[/yellow] Run [bold]devlog start[/bold] first.")
            return
        active.end_time = datetime.now(timezone.utc)
        db.commit()
        db.refresh(active)
        console.print(f"[green]Stopped:[/green] {active.description}")
        console.print(f"[dim]Duration: {active.duration_minutes} min[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
    finally:
        db.close()
