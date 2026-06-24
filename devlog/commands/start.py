import click
from rich.console import Console
from devlog.db import get_session
from devlog.models import Session

console = Console()


def start_session(description: str):
    db = get_session()
    try:
        active = db.query(Session).filter(Session.end_time.is_(None)).first()
        if active:
            console.print(
                f"[yellow]Session already active:[/yellow] {active.description}\n"
                "Run [bold]devlog stop[/bold] first."
            )
            return
        session = Session(description=description)
        db.add(session)
        db.commit()
        db.refresh(session)
        console.print(f"[green]Started:[/green] {description}")
        console.print(f"[dim]Session ID: {session.id}[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
    finally:
        db.close()
