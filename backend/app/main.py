from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database.session import engine
from app.middleware.error_handler import register_exception_handlers
from app.api import auth as auth_router
from app.api import cases as cases_router

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router.router)
app.include_router(cases_router.router)


@app.get("/health", tags=["system"])
def health():
    """Liveness check — does the process respond at all."""
    return {"status": "ok"}


@app.get("/ready", tags=["system"])
def ready():
    """Readiness check — can we actually reach the database."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        return {"status": "not_ready", "database": "unreachable"}
