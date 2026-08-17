from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.services.pipeline import load_models
from app.routers import predict, insight

BASE_DIR = Path(__file__).parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()
    yield


app = FastAPI(
    title="E-Commerce Churn Prediction",
    description="Dashboard prediksi churn pelanggan berbasis XGBoost",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Disable Jinja2 LRU cache (incompatible with Starlette 1.2+ dict-key globals)
_jinja_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=select_autoescape(["html"]),
    auto_reload=True,
)
_jinja_env.cache = None  # type: ignore[assignment]
templates = Jinja2Templates(env=_jinja_env)

app.include_router(predict.router)
app.include_router(insight.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@app.get("/predict", response_class=HTMLResponse, include_in_schema=False)
async def predict_page(request: Request):
    return templates.TemplateResponse(request, "predict.html")


@app.get("/result", response_class=HTMLResponse, include_in_schema=False)
async def result_page(request: Request):
    return templates.TemplateResponse(request, "result.html")
