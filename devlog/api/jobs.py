import asyncio
from datetime import datetime, timezone

from devlog.db import get_session
from devlog.models import Session


async def hourly_summary():
    """Logs a count of today's sessions every hour.
    In production this is where you'd send a Slack message or email digest.
    """
    while True:
        await asyncio.sleep(3600)
        db = get_session()
        try:
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            sessions = db.query(Session).filter(Session.start_time >= today).all()
            completed = [s for s in sessions if s.end_time]
            total_min = sum(s.duration_minutes or 0 for s in completed)
            print(
                f"[DevLog] Hourly digest — {len(sessions)} session(s) today, "
                f"{round(total_min / 60, 1)}h logged",
                flush=True,
            )
        except Exception as e:
            print(f"[DevLog] Background job error: {e}", flush=True)
        finally:
            db.close()
