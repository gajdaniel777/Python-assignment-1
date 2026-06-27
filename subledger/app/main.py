from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal, init_db
from app.exceptions import SubLedgerError
from app.routes import customers, invoices, payments, plans, subscriptions


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_title, version=settings.app_version, lifespan=lifespan)


@app.middleware("http")
async def db_transaction_middleware(request: Request, call_next):
    response = await call_next(request)
    db: Session | None = getattr(request.state, "db", None)
    if db is not None:
        if 200 <= response.status_code < 400:
            db.commit()
        else:
            db.rollback()
        db.close()
    return response


@app.middleware("http")
async def attach_db_session(request: Request, call_next):
    db = SessionLocal()
    request.state.db = db
    response = await call_next(request)
    return response


@app.exception_handler(SubLedgerError)
async def subledger_error_handler(request: Request, exc: SubLedgerError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(plans.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")
app.include_router(payments.router, prefix="/api")


@app.get("/")
def root():
    return {
        "app": settings.app_title,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "api_base": "/api",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
