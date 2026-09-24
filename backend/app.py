from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import get_settings
from database.database import init_db
from routes.analytics import router as analytics_router
from routes.iot import router as iot_router
from routes.prediction import router as prediction_router
from services.model_service import load_model_artifacts, model_ready
from services.prediction_service import DISCLAIMER

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ovarian-ai")
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    load_model_artifacts()
    logger.info("Model, scaler, and database ready.")
    yield


app = FastAPI(
    title="Ovarian Cancer AI – Smart IoT Clinical Risk Detection System",
    description=(
        "Academic/research prototype for demonstrating clinical-metadata deep learning "
        "connected to an ESP32 IoT node. Not for clinical diagnosis."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediction_router)
app.include_router(iot_router)
app.include_router(analytics_router)

uploads = Path(__file__).resolve().parent / "uploads"
uploads.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads), name="uploads")


@app.middleware("http")
async def request_logger(request: Request, call_next):
    logger.info("%s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("Completed %s %s -> %s", request.method, request.url.path, response.status_code)
    return response


@app.exception_handler(Exception)
async def unhandled_error(_: Request, exc: Exception):
    if isinstance(exc, (HTTPException, StarletteHTTPException)):
        raise exc
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Server error. Check backend logs."})


@app.get("/", tags=["System"])
def root():
    return {
        "name": settings.app_name,
        "status": "online",
        "docs": "/docs",
        "disclaimer": DISCLAIMER,
        "banner": "Prototype for Research & Demonstration – Not for Clinical Diagnosis",
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "api": "online",
        "model_loaded": model_ready(),
        "environment": settings.app_env,
    }
