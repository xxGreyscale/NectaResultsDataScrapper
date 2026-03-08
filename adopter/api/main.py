from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler

from adopter.api.models import ErrorDetail
from adopter.api.response_utils import error_response
from adopter.api.routers import centers, exports, health, jobs, meta, results, summaries
from adopter.api.storage_setup import setup_api_indexes
from adopter.api.job_queue import enqueue_job
from infastructure import settings


def create_app() -> FastAPI:
    app = FastAPI(title="NECTA API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    def _validation_exception_handler(_request, exc: RequestValidationError):
        errors = []
        for item in exc.errors():
            loc = ".".join(str(part) for part in item.get("loc", []))
            errors.append(ErrorDetail(code="validation_error", message=item.get("msg", "Invalid input"), field=loc))
        payload = error_response(errors, meta={"type": "validation"})
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(Exception)
    def _unhandled_exception_handler(_request, exc: Exception):
        if hasattr(exc, "status_code") and hasattr(exc, "detail"):
            detail = getattr(exc, "detail")
            message = detail if isinstance(detail, str) else "Request failed"
            payload = error_response([ErrorDetail(code=str(getattr(exc, "status_code")), message=message)])
            return JSONResponse(status_code=getattr(exc, "status_code"), content=payload.model_dump())
        payload = error_response([ErrorDetail(code="internal_error", message="Internal server error")])
        return JSONResponse(status_code=500, content=payload.model_dump())

    app.include_router(health.router, prefix="/v1")
    app.include_router(meta.router, prefix="/v1")
    app.include_router(centers.router, prefix="/v1")
    app.include_router(results.router, prefix="/v1")
    app.include_router(summaries.router, prefix="/v1")
    app.include_router(jobs.router, prefix="/v1")
    app.include_router(exports.router, prefix="/v1")

    def _schedule_jobs() -> None:
        if not settings.SCHEDULER_ENABLED:
            return

        scheduler = BackgroundScheduler(timezone="UTC")

        def _enqueue_all() -> None:
            from infastructure.database_config import get_database

            db = get_database(settings.MONGO_URI, settings.DB_NAME)
            for exam_type in settings.SCHEDULER_EXAM_TYPES:
                if not settings.SCHEDULER_YEARS:
                    continue
                payload = {
                    "type": "results",
                    "examType": exam_type,
                    "years": settings.SCHEDULER_YEARS,
                    "sourceUrl": settings.SCHEDULER_SOURCE_URL,
                    "priority": 1,
                    "idempotencyKey": f"scheduler|{exam_type}|{settings.SCHEDULER_YEARS}|{settings.SCHEDULER_SOURCE_URL}",
                }
                enqueue_job(db, payload)

        scheduler.add_job(_enqueue_all, "interval", seconds=settings.SCHEDULER_INTERVAL_SECONDS)
        scheduler.start()

    @app.on_event("startup")
    def _startup() -> None:
        setup_api_indexes()
        _schedule_jobs()

    return app


app = create_app()
