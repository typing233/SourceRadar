import logging
import os

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app import models
from app.routers import auth, items, tags, digest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables
    os.makedirs("data", exist_ok=True)
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Start background scheduler
    from app.services.scheduler import start_scheduler, run_crawlers
    scheduler = start_scheduler()

    # Initial crawl on startup (non-blocking, best effort)
    import threading
    t = threading.Thread(target=run_crawlers, daemon=True)
    t.start()

    yield

    scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down")


app = FastAPI(title="SourceRadar API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(tags.router)
app.include_router(digest.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
