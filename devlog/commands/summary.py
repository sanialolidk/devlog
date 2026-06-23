from datetime import datetime, timezone, timedelta
from rich.console import Console
from rich.markdown import Markdown
from devlog.db import get_session
from devlog.models import Session

console = Console()


def ai_summary(period: str):
    try:
        import anthropic
    except ImportError:
        console.print(
            "[red]anthropic package not installed.[/red] "
            "Run: [bold]pip install anthropic[/bold]"
        )
        return

    db = get_session()
    now = datetime.now(timezone.utc)

    if period == "today":
        since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        label = "today"
    else:
        since = now - timedelta(days=7)
        label = "the last 7 days"

    sessions = (
        db.query(Session)
        .filter(Session.start_time >= since)
        .order_by(Session.start_time.asc())
        .all()
    )

    lines = []
    for s in sessions:
        tags = ", ".join(t.name for t in s.tags) or "none"
        dur = f"{s.duration_minutes} min" if s.end_time else "still active"
        started = s.start_time.strftime("%b %d %H:%M")
        lines.append(f"- [{started}] {s.description} ({dur}) [tags: {tags}]")

    db.close()

    if not lines:
        console.print(f"[dim]No sessions found for {label}.[/dim]")
        return

    context = "\n".join(lines)
    prompt = (
        f"Here are my dev sessions from {label}:\n\n{context}\n\n"
        "Please give me a concise summary of what I worked on, "
        "highlighting key themes, progress made, and any patterns you notice. "
        "Keep it encouraging and actionable."
    )

    console.print(f"\n[dim]Summarizing {len(lines)} session(s) with Claude...[/dim]\n")

    client = anthropic.Anthropic()

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=1024,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        message = stream.get_final_message()

    for block in message.content:
        if block.type == "text":
            console.print(Markdown(block.text))
