import csv
import json
import sys
from datetime import datetime, timezone, timedelta
from rich.console import Console
from devlog.db import get_session
from devlog.models import Session

console = Console()


def export_sessions(fmt: str, period: str, output: str):
    db = get_session()
    now = datetime.now(timezone.utc)

    query = db.query(Session).order_by(Session.start_time.asc())
    if period == "today":
        since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(Session.start_time >= since)
    elif period == "week":
        query = query.filter(Session.start_time >= now - timedelta(days=7))

    sessions = query.all()

    rows = [
        {
            "id": s.id,
            "description": s.description,
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "duration_minutes": s.duration_minutes,
            "is_active": s.is_active,
            "tags": [t.name for t in s.tags],
        }
        for s in sessions
    ]
    db.close()

    if not rows:
        console.print("[dim]No sessions to export.[/dim]")
        return

    dest = open(output, "w", newline="", encoding="utf-8") if output else sys.stdout

    try:
        if fmt == "json":
            json.dump(rows, dest, indent=2)
            if output:
                dest.write("\n")
        else:
            fieldnames = ["id", "description", "start_time", "end_time",
                          "duration_minutes", "is_active", "tags"]
            writer = csv.DictWriter(dest, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                row = dict(row)
                row["tags"] = "|".join(row["tags"])
                writer.writerow(row)
    finally:
        if output:
            dest.close()

    if output:
        console.print(
            f"[green]Exported {len(rows)} session(s) to [bold]{output}[/bold] "
            f"({fmt.upper()})[/green]"
        )
