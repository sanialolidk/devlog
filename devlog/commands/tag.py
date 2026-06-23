from rich.console import Console
from devlog.db import get_session
from devlog.models import Session, Tag

console = Console()


def tag_session(tags: tuple[str]):
    db = get_session()

    # Tag the most recently started session (active or last completed)
    session = (
        db.query(Session)
        .order_by(Session.start_time.desc())
        .first()
    )
    if not session:
        console.print("[yellow]No sessions found.[/yellow] Run [bold]devlog start[/bold] first.")
        db.close()
        return

    added = []
    for name in tags:
        name = name.lower().strip()
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
        if tag not in session.tags:
            session.tags.append(tag)
            added.append(name)

    db.commit()
    tag_list = ", ".join(f"[cyan]{t}[/cyan]" for t in added) if added else "[dim](already tagged)[/dim]"
    console.print(f"[green]Tagged[/green] \"{session.description}\" with {tag_list}")
    db.close()
