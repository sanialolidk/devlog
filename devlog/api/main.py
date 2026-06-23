import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from devlog.api.limiter import limiter
from devlog.api.jobs import hourly_summary
from devlog.api.routes import sessions, tags, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(hourly_summary())
    yield
    task.cancel()


app = FastAPI(title="DevLog API", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*\.vercel\.app|http://localhost:\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])


@app.get("/health")
def health():
    return {"status": "ok"}
