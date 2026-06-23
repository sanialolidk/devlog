from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from devlog.api.routes import sessions, tags

app = FastAPI(title="DevLog API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])


@app.get("/health")
def health():
    return {"status": "ok"}
