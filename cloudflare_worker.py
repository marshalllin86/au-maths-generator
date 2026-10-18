"""Cloudflare Workers entry point for the web worksheet generator."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel
from workers import asgi

from worksheet import SINGLE_CATEGORIES, make_worksheet


app = FastAPI(title="Daily Practice", docs_url=None, redoc_url=None, openapi_url=None)


class WorksheetRequest(BaseModel):
    category: str


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/categories")
async def categories() -> list[dict[str, str]]:
    return [{"label": label, "value": value} for label, value in SINGLE_CATEGORIES.items()]


@app.get("/api/config")
async def client_config(request: Request) -> dict[str, str | None]:
    env = request.scope["env"]
    return {
        "supabaseUrl": getattr(env, "SUPABASE_URL", None),
        "supabasePublishableKey": getattr(env, "SUPABASE_PUBLISHABLE_KEY", None),
    }


@app.post("/api/worksheet")
async def generate_worksheet(payload: WorksheetRequest) -> dict[str, object]:
    if payload.category not in set(SINGLE_CATEGORIES.values()):
        raise HTTPException(status_code=422, detail="Choose a supported worksheet topic")
    single, mixed = make_worksheet(payload.category)
    return {
        "single": [question.__dict__ for question in single],
        "mixed": [question.__dict__ for question in mixed],
    }


async def _static_asset(request: Request, path: str) -> Response:
    env = request.scope["env"]
    asset_url = f"https://assets.local/{path}"
    asset_response = await env.ASSETS.fetch(asset_url)
    return Response(
        content=await asset_response.bytes(),
        status_code=asset_response.status,
        headers=asset_response.headers,
    )


@app.get("/")
async def homepage(request: Request) -> Response:
    return await _static_asset(request, "")


@app.get("/{path:path}")
async def frontend(path: str, request: Request) -> Response:
    return await _static_asset(request, path)


Default = asgi.entrypoint(app)
