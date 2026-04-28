import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import auth, content, users, reports
from .services.scheduler import create_scheduler, run_scrapers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    init_db()

    logger.info("Starting scheduler...")
    scheduler = create_scheduler()
    scheduler.start()

    logger.info("Running initial scrape...")
    import threading
    scrape_thread = threading.Thread(target=run_scrapers, daemon=True)
    scrape_thread.start()

    yield

    logger.info("Shutting down scheduler...")
    scheduler.shutdown()


app = FastAPI(
    title="SourceRadar API",
    description="Personalized project discovery tool for developers",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
