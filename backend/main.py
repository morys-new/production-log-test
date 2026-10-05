from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import asyncpg
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db.client import close_pool, create_pool
from errors import ApiError, api_error_handler, validation_error_handler
from routers.entries import router as entries_router
from routers.health import router as health_router
from routers.pits import router as pits_router
from routers.summary import router as summary_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    database_url = get_settings().database_url
    try:
        await create_pool(database_url)
    except (OSError, asyncpg.PostgresError) as exc:
        target = urlparse(database_url)
        raise RuntimeError(
            f"Cannot connect to Postgres at {target.hostname}:{target.port} "
            f"(database '{target.path.lstrip('/')}'): {exc}\n"
            "Is Postgres running? Try: docker compose up -d prodlog-db"
        ) from None
    yield
    await close_pool()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="ProdLog API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(ApiError, api_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        RequestValidationError,
        validation_error_handler,  # type: ignore[arg-type]
    )
    app.include_router(health_router)
    app.include_router(pits_router)
    app.include_router(entries_router)
    app.include_router(summary_router)

    return app


app = create_app()
