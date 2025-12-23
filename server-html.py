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


mcp = FastMCP(name="minimal-mcp", stateless_http=True)


@mcp._mcp_server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="show-widget",
            title="Show Widget",
            description="Render the example widget.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pizzaTopping": {"type": "string"}
                },
                "required": ["pizzaTopping"],
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


async def call_tool(req: types.CallToolRequest):
    args = req.params.arguments or {}
    topping = args.get("pizzaTopping", "")

    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Widget rendered!")],
            structuredContent={"pizzaTopping": topping},
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool

app = mcp.streamable_http_app()

# Uncomment this block block is for MCP Jam to test the widget
# from mcp.types import SetLevelRequest, ServerResult, EmptyResult
#
#
# async def set_logging_level(req: SetLevelRequest):
#     level = req.params.level if req.params else None
#     print(f"[MCP] Logging level set to: {level}")
#     # Return an empty result wrapped in ServerResult
#     return ServerResult(EmptyResult())
#
#
# mcp._mcp_server.request_handlers[types.SetLevelRequest] = set_logging_level
#
#
# from fastapi.middleware.cors import CORSMiddleware
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.requests import Request
#
# class CSPMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         response = await call_next(request)
#         response.headers["Content-Security-Policy"] = "frame-ancestors *"
#         return response


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://127.0.0.1:6274/", "http://localhost:6274"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# app.add_middleware(CSPMiddleware)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
