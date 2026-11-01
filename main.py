"""Warranty Watch FastAPI application entrypoint."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal, init_db
from notification_service import regenerate_notifications
from routes import (
    activity,
    assistant,
    dashboard,
    monitors,
    notifications,
    products,
    recalls,
    service_requests,
    settings,
    tinyfish,
    warranty,
)

ROUTERS = [
    products,
    dashboard,
    warranty,
    assistant,
    service_requests,
    recalls,
    notifications,
    monitors,
    activity,
    settings,
    tinyfish,
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        regenerate_notifications(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Warranty Watch API", version="1.0.0", lifespan=lifespan)

# Permissive CORS for local development (frontend on a separate Vite port).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in ROUTERS:
    app.include_router(module.router)


@app.get("/api/health")
def root_health():
    return {"status": "ok", "service": "Warranty Watch API"}
