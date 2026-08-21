"""API v1 router registry."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.machines import router as machines_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(machines_router)

