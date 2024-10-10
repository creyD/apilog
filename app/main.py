import os
from contextlib import asynccontextmanager

from creyPY.fastapi.app import generate_unique_id
from dotenv import load_dotenv
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.services.auth import verify

load_dotenv()

ENV = os.getenv("ENV", "local").lower()
VERSION = os.getenv("VERSION", "Alpha")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.setup import setup

    setup()

    # Create initial API key
    from creyPY.fastapi.db.session import get_db
    from sqlalchemy.orm import Session

    from app.models.auth import APIKey

    db: Session = next(get_db())
    key_obj = db.query(APIKey).filter(APIKey.note == "local_key").one_or_none()
    if not key_obj:
        db.add(APIKey(note="local_key"))  # type: ignore
        db.commit()
        key_obj = db.query(APIKey).filter(APIKey.note == "local_key").one()
    print(f"Local API key: {key_obj.id}")
    yield


# App Setup
app = FastAPI(
    title="ApiLog API",
    description="Tiny service for ingesting logs via POST and querying them via GET.",
    version=VERSION,
    docs_url="/",
    redoc_url=None,
    debug=ENV != "prod",
    swagger_ui_parameters={
        "docExpansion": "list",
        "displayOperationId": True,
        "defaultModelsExpandDepth": 5,
        "defaultModelExpandDepth": 5,
        "filter": True,
        "displayRequestDuration": True,
        "defaultModelRendering": "model",
        "persistAuthorization": True,
    },
    generate_unique_id_function=generate_unique_id,
    dependencies=[Security(verify)],
    lifespan=lifespan,
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:4200",
]

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# App Routers
from app.routes.app import router as app_router
from app.routes.entry import router as entry_router

app.include_router(app_router)
app.include_router(entry_router)


# Pagination
add_pagination(app)
