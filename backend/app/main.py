"""FastAPI application factory and instance."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.services.errors import (
    DuplicateDeviceIdError,
    DuplicateUserEmailError,
    ImplementNotFoundError,
    InvalidJobStateTransitionError,
    InvalidWorkingWidthError,
    JobNotFoundError,
    MachineNotFoundError,
    OrganizationNotFoundError,
)


def create_app() -> FastAPI:
    """Create and configure the AgroData FastAPI application."""

    application = FastAPI(
        title="AgroData API",
        version="0.1.0",
        description="AgroData backend service API",
    )

    @application.exception_handler(MachineNotFoundError)
    async def machine_not_found_handler(
        request: Request,
        exc: MachineNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @application.exception_handler(ImplementNotFoundError)
    async def implement_not_found_handler(
        request: Request,
        exc: ImplementNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @application.exception_handler(JobNotFoundError)
    async def job_not_found_handler(
        request: Request,
        exc: JobNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @application.exception_handler(InvalidJobStateTransitionError)
    async def invalid_job_state_transition_handler(
        request: Request,
        exc: InvalidJobStateTransitionError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @application.exception_handler(InvalidWorkingWidthError)
    async def invalid_working_width_handler(
        request: Request,
        exc: InvalidWorkingWidthError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    @application.exception_handler(OrganizationNotFoundError)
    async def organization_not_found_handler(
        request: Request,
        exc: OrganizationNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @application.exception_handler(DuplicateDeviceIdError)
    async def duplicate_device_id_handler(
        request: Request,
        exc: DuplicateDeviceIdError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @application.exception_handler(DuplicateUserEmailError)
    async def duplicate_user_email_handler(
        request: Request,
        exc: DuplicateUserEmailError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    application.include_router(api_v1_router)

    return application


app = create_app()

