from pathlib import Path
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).parent

DIST_WIDGET_DIR = ROOT / "dist" / "widgets" / "greeting-widget"

DEV_WIDGET_HTML = ROOT / "widgets" / "greeting-widget" / "index.html"

MIME_TYPE = "text/html+skybridge"
WIDGET_URI = "ui://widget/greeting-widget.html"

mcp = FastMCP(name="minimal-react-mcp", stateless_http=True)


class WidgetInput(BaseModel):
    name: str = Field(..., description="Name to greet.")


@mcp._mcp_server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="show-greeting-widget",
            title="Show Greeting React Widget",
            description="Render the Vite-built React greeting widget.",
            inputSchema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
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
            name="greeting-widget",
            title="Greeting Widget",
            uri=WIDGET_URI,
            description="Vite-built React widget HTML.",
            mimeType=MIME_TYPE,
        )
    ]


def find_widget_html() -> Path | None:
    """
    Returns the final widget HTML file:
    - First: the Vite-built hashed HTML in dist/widgets/greeting-widget/
    - Otherwise: fall back to dev index.html
    """
    if DIST_WIDGET_DIR.exists():
        html_files = list(DIST_WIDGET_DIR.glob("*.html"))
        if html_files:
            return html_files[0]

    if DEV_WIDGET_HTML.exists():
        return DEV_WIDGET_HTML

    return None


async def handle_resource(req: types.ReadResourceRequest):
    html = find_widget_html()
    if not html:
        return types.ServerResult(types.ReadResourceResult(contents=[]))

    # Read built HTML exactly as-is. It already includes <script type="module"> tags.
    text = html.read_text(encoding="utf8")

    return types.ServerResult(
        types.ReadResourceResult(
            contents=[
                types.TextResourceContents(
                    uri=WIDGET_URI,
                    mimeType=MIME_TYPE,
                    text=text,
                )
            ]
        )
    )


mcp._mcp_server.request_handlers[types.ReadResourceRequest] = handle_resource


async def call_tool(req: types.CallToolRequest):
    args = req.params.arguments or {}
    name = args.get("name", "")

    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text="Widget rendered!")],
            structuredContent={"name": name},
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool

#app = FastAPI()

#app.mount("/static", StaticFiles(directory="dist"), name="static")

# app.mount("/mcp", mcp.streamable_http_app())
app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# from pathlib import Path
# import mcp.types as types
# from mcp.server.fastmcp import FastMCP
# from pydantic import BaseModel, Field
#
# DIST_WIDGETS_DIR = Path(__file__).parent / "dist" / "widgets" / "greeting-widget"
#
# DEV_WIDGET_PATH = Path(__file__).parent / "widgets" / "greeting-widget" / "index.html"
#
# MIME_TYPE = "text/html+skybridge"
# WIDGET_URI = "ui://widget/greeting-widget.html"
#
# mcp = FastMCP(name="minimal-react-mcp", stateless_http=True)
#
#
# class WidgetInput(BaseModel):
#     name: str = Field(..., description="Name to greet.")
#
#
# @mcp._mcp_server.list_tools()
# async def list_tools():
#     return [
#         types.Tool(
#             name="show-greeting-widget",
#             title="Show Greeting React Widget",
#             description="Render a React + Vite widget.",
#             inputSchema={
#                 "type": "object",
#                 "properties": {"name": {"type": "string"}},
#                 "required": ["name"],
#             },
#             _meta={
#                 "openai/outputTemplate": WIDGET_URI,
#                 "openai/widgetAccessible": True,
#                 "openai/resultCanProduceWidget": True,
#             },
#         )
#     ]
#
#
# @mcp._mcp_server.list_resources()
# async def list_resources():
#     return [
#         types.Resource(
#             name="greeting-widget",
#             title="Greeting Widget",
#             uri=WIDGET_URI,
#             description="Greeting widget HTML built by Vite.",
#             mimeType=MIME_TYPE,
#         )
#     ]
#
#
# def find_built_widget_html() -> Path | None:
#     """
#     Look for greeting-widget.*.html inside the Vite build output.
#     If not found, return DEV_WIDGET_PATH if it exists.
#     """
#     if DIST_WIDGETS_DIR.exists():
#         matches = list(DIST_WIDGETS_DIR.glob("*.html"))
#         if matches:
#             return matches[0]
#     if DEV_WIDGET_PATH.exists():
#         return DEV_WIDGET_PATH
#     return None
#
#
# async def handle_resource(req: types.ReadResourceRequest):
#     html_path = find_built_widget_html()
#     if not html_path:
#         return types.ServerResult(types.ReadResourceResult(contents=[]))
#
#     text = html_path.read_text(encoding="utf8")
#     return types.ServerResult(
#         types.ReadResourceResult(
#             contents=[
#                 types.TextResourceContents(
#                     uri=WIDGET_URI,
#                     mimeType=MIME_TYPE,
#                     text=text,
#                 )
#             ]
#         )
#     )
#
#
# mcp._mcp_server.request_handlers[types.ReadResourceRequest] = handle_resource
#
#
# async def call_tool(req: types.CallToolRequest):
#     args = req.params.arguments or {}
#     name = args.get("name", "")
#
#     return types.ServerResult(
#         types.CallToolResult(
#             content=[types.TextContent(type="text", text="Widget rendered!")],
#             structuredContent={"name": name},
#         )
#     )
#
#
# mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool
#
# app = mcp.streamable_http_app()
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)
