import os
from mmap import MAP_SHARED
from pathlib import Path

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from functools import lru_cache
import urllib.request
import urllib.error

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route
from starlette.staticfiles import StaticFiles


ASSETS_DIR = Path(__file__).parent / "assets"
BASE_URI = os.getenv("BASE_URI", "https://untaxied-subintroductive-sadye.ngrok-free.dev").rstrip("/")
ASSETS_BASE_URI = f"{BASE_URI}/assets" if BASE_URI else ""

MIME_TYPE = "text/html+skybridge"
MAP_URI = "ui://widget/map-v2.html"

mcp = FastMCP(name="app", stateless_http=True)

@lru_cache(maxsize=None)
def _load_widget_html(component_name: str) -> str:
    if ASSETS_BASE_URI:
        url = f"{ASSETS_BASE_URI}/{component_name}.html"
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset, errors="replace")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            pass

    local = ASSETS_DIR / f"{component_name}.html"
    if local.exists():
        return local.read_text(encoding="utf8")
    hashed = sorted(ASSETS_DIR.glob(f"{component_name}-*.html"))
    if hashed:
        return hashed[-1].read_text(encoding="utf8")
    raise FileNotFoundError(f'Widget HTML "{component_name}" not found in {ASSETS_DIR} or {ASSETS_BASE_URI or "(no remote)"}')


@mcp._mcp_server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="book-table",
            title="Book table",
            description="Book table in a restaurant for provided location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string",
                                 "description": "Initial location to focus (e.g. berlin, erode, chennai)"},
                },
            },
            _meta={
                "openai/outputTemplate": MAP_URI,
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True,
            },
        )
    ]

@mcp._mcp_server.list_resources()
async def list_resources():
    return [
        types.Resource(
            name="map-widget",
            title="Map Widget",
            uri=MAP_URI,
            description="Map widget HTML.",
            mimeType=MIME_TYPE,
        )
    ]

async def handle_resource(req: types.ReadResourceRequest):
    print(f"DEBUG: Resource requested: {req.params.uri}")
    try:
        html_text = _load_widget_html("map")
    except Exception as e:
        html_text = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Example Widget</title></head>
<body>
  <pre style="white-space:pre-wrap;color:#b91c1c;background:#fff0f0;padding:12px;border:1px solid #fca5a5;border-radius:6px">
[Assets] Failed to load widget HTML.
{type(e).__name__}: {e}
Tried: {ASSETS_BASE_URI or "(no remote)"} and {ASSETS_DIR}.
  </pre>
</body></html>"""

    if BASE_URI:
        html_text = html_text.replace("__BASE_URI__", BASE_URI)


    return types.ServerResult(
        types.ReadResourceResult(
            contents=[
                types.TextResourceContents(
                    uri=MAP_URI,
                    mimeType=MIME_TYPE,
                    text=html_text,
                )
            ]
        )
    )
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = handle_resource

async def call_tool(req: types.CallToolRequest):
    name = req.params.name
    print(f"Received tool call: {name}")
    args = req.params.arguments or {}
    location = args.get("location")
    print(f"Location: {location}")
    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text="Booking widget rendered")],
            structuredContent={
                "location": location,
            },
        )
    )
mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool

app = mcp.streamable_http_app()

async def health(request):
    return JSONResponse({"status": "ok"})

app.routes.append(Route("/health", endpoint=health))

# Allow cross-origin requests (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # or ["http://localhost:8000"] for stricter
    allow_methods=["GET","POST", "OPTIONS"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR), html=False), name="assets")


class BookingPayload(BaseModel):
    restaurantName: str
    numPersons: int
    date: str
    time: str

try:
    from google.cloud import firestore
    project_id = os.environ.get("GOOGLE_PROJECT_ID", "test-project")
    database = "chatnative"
    db = firestore.Client(project=project_id, database=database)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Firestore client: {e}")

async def create_booking(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"detail": "Invalid JSON body"}, status_code=400)

    try:
        payload = BookingPayload(**body)
    except Exception as e:
        return JSONResponse({"detail": f"Validation error: {e}"}, status_code=422)

    try:
        doc = {
            "restaurantName": payload.restaurantName,
            "numPersons": payload.numPersons,
            "date": payload.date,
            "time": payload.time,
            "createdAt": firestore.SERVER_TIMESTAMP,
        }
        _, ref = db.collection("bookings").add(doc)
        return JSONResponse({"status": "ok", "id": ref.id})
    except Exception as e:
        return JSONResponse({"detail": f"Failed to save booking: {e}"}, status_code=500)

app.add_route("/api/bookings", create_booking, methods=["POST", "OPTIONS"])


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host=host, port=port)