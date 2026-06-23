from datetime import datetime, timezone
from rich.console import Console
from devlog.db import get_session
from devlog.models import Session

console = Console()


def resume_session(session_id: int):
    db = get_session()

    original = db.query(Session).filter(Session.id == session_id).first()
    if not original:
        console.print(f"[red]Session {session_id} not found.[/red]")
        db.close()
        return

    active = db.query(Session).filter(Session.end_time.is_(None)).first()
    if active:
        console.print(
            f"[yellow]Session #{active.id} is still active. Stop it first with `devlog stop`.[/yellow]"
        )
        db.close()
        return

    new_session = Session(
        description=original.description,
        start_time=datetime.now(timezone.utc),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    console.print(
        f"[green]Resumed:[/green] [bold]{new_session.description}[/bold] "
        f"[dim](new session #{new_session.id}, copied from #{session_id})[/dim]"
    )
    db.close()
