from fastapi import FastAPI
from devlog.api.routes import sessions, tags

app = FastAPI(title="DevLog API", version="0.1.0")

app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])


@app.get("/health")
def health():
    return {"status": "ok"}
