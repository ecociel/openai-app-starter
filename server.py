import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import mcp.types as types
from pydantic import BaseModel, Field

HTML_PATH = Path(__file__).parent / "widget.html"
HTML_TEXT = HTML_PATH.read_text(encoding="utf8")

MIME_TYPE = "text/html+skybridge"
WIDGET_URI = "ui://widget/example.html"


class WidgetInput(BaseModel):
    pizzaTopping: str = Field(..., description="Topping to render.")
    cheeseType: str = Field(..., description="Cheese type to render.")


mcp = FastMCP(name="minimal-mcp", stateless_http=True)

#
# @mcp._mcp_server.list_tools()
# async def list_tools():
#     return [
#         types.Tool(
#             name="show-widget",
#             title="Show Widget",
#             description="Render the example widget.",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "pizzaTopping": {"type": "string"},
#                     "cheeseType": {"type": "string"},
#                 },
#                 "required": ["pizzaTopping", "cheeseType"],
#             },
#             _meta={
#                 "openai/outputTemplate": WIDGET_URI,
#                 "openai/widgetAccessible": True,
#                 "openai/resultCanProduceWidget": True,
#             },
#         )
#     ]

@mcp._mcp_server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="book-table",
            title="Book Table",
            description="Open the table booking form (restaurant, persons, date, time).",
            inputSchema={
                "type": "object",
                "properties": {
                    "restaurantName": {"type": "string"},
                    "numPersons": {"type": "integer", "minimum": 1},
                    "date": {"type": "string", "format": "date"},
                    "time": {"type": "string", "format": "time"},
                },
                # No required fields — form loads without arguments
            },
            _meta={
                "openai/outputTemplate": WIDGET_URI,
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True,
            },
        )
    ]



@mcp._mcp_server.list_resources()
async def list_resources():
    return [
        types.Resource(
            name="example-widget",
            title="Example Widget",
            uri=WIDGET_URI,
            description="Example widget HTML.",
            mimeType=MIME_TYPE,
        )
    ]


async def handle_resource(req: types.ReadResourceRequest):
    return types.ServerResult(
        types.ReadResourceResult(
            contents=[
                types.TextResourceContents(
                    uri=WIDGET_URI,
                    mimeType=MIME_TYPE,
                    text=HTML_TEXT,
                )
            ]
        )
    )


mcp._mcp_server.request_handlers[types.ReadResourceRequest] = handle_resource


# async def call_tool(req: types.CallToolRequest):
#     args = req.params.arguments or {}
#     topping = args.get("pizzaTopping", "")
#     cheese = args.get("cheeseType", "")
#
#     return types.ServerResult(
#         types.CallToolResult(
#             content=[types.TextContent(type="text", text=f"Widget rendered!")],
#             structuredContent={
#                 "pizzaTopping": topping,
#                 "cheeseType": cheese,
#             },
#         )
#     )

async def call_tool(req: types.CallToolRequest):
    args = req.params.arguments or {}
    restaurant_name = args.get("restaurantName")
    num_persons = args.get("numPersons")
    date = args.get("date")
    time = args.get("time")

    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text="Booking widget rendered")],
            structuredContent={
                "restaurantName": restaurant_name,
                "numPersons": num_persons,
                "date": date,
                "time": time,
            },
        )
    )



mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool

app = mcp.streamable_http_app()

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# Allow cross-origin requests (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # or ["http://localhost:8000"] for stricter
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


class BookingPayload(BaseModel):
    restaurantName: str
    numPersons: int
    date: str
    time: str

# Initialize Firestore at startup; fail fast if misconfigured
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

# Register Starlette route directly (no FastAPI router)
app.add_route("/api/bookings", create_booking, methods=["POST", "OPTIONS"])
# --- end Starlette route ---


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)