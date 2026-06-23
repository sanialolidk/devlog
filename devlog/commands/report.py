from datetime import datetime, timezone, timedelta
from collections import Counter
from rich.console import Console
from rich.table import Table
from devlog.db import get_session
from devlog.models import Session

console = Console()


def report_sessions(period: str):
    db = get_session()
    now = datetime.now(timezone.utc)

    if period == "today":
        since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        label = "Today"
    else:
        since = now - timedelta(days=7)
        label = "Last 7 days"

    sessions = (
        db.query(Session)
        .filter(Session.start_time >= since)
        .order_by(Session.start_time.asc())
        .all()
    )

    if not sessions:
        db.close()
        console.print(f"[dim]No sessions in {label.lower()}.[/dim]")
        return

    completed = [s for s in sessions if s.end_time]
    active = [s for s in sessions if s.is_active]
    total_minutes = sum(s.duration_minutes for s in completed)

    tag_counter = Counter()
    for s in sessions:
        for t in s.tags:
            tag_counter[t.name] += 1

    rows = [
        (str(s.id), s.description, s.end_time, s.duration_minutes,
         [t.name for t in s.tags])
        for s in sessions
    ]
    db.close()

    hours, mins = divmod(int(total_minutes), 60)

    console.print(f"\n[bold magenta]DevLog Report — {label}[/bold magenta]\n")

    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="dim")
    summary.add_column(style="bold")
    summary.add_row("Sessions", str(len(rows)))
    summary.add_row("Completed", str(len(completed)))
    summary.add_row("Active", str(len(active)))
    summary.add_row("Total time", f"{hours}h {mins}m" if hours else f"{mins}m")
    console.print(summary)

    if tag_counter:
        console.print("\n[bold]Top tags:[/bold]")
        tag_table = Table(show_header=False, box=None, padding=(0, 2))
        tag_table.add_column(style="green")
        tag_table.add_column(style="dim", justify="right")
        for name, count in tag_counter.most_common(5):
            tag_table.add_row(name, f"{count} session{'s' if count != 1 else ''}")
        console.print(tag_table)

    console.print("\n[bold]Sessions:[/bold]")
    sess_table = Table(show_header=True, header_style="bold")
    sess_table.add_column("ID", style="dim", width=4)
    sess_table.add_column("Description", min_width=25)
    sess_table.add_column("Duration", justify="right")
    sess_table.add_column("Tags", style="green")
    for sid, desc, end_time, dur_min, tag_names in rows:
        dur = f"{dur_min} min" if end_time else "[green]active[/green]"
        tags = ", ".join(tag_names) or "—"
        sess_table.add_row(sid, desc, dur, tags)
    console.print(sess_table)
    console.print()
