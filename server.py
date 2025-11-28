from pathlib import Path
import mcp.types as types
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent

DIST_WIDGET_DIR = ROOT / "dist" / "widgets" / "greeting-widget"
DEV_WIDGET_HTML = ROOT / "widgets" / "greeting-widget" / "index.html"

WIDGET_URI = "ui://widget/greeting-widget.html"
ASSETS_URI = "ui://widget/greeting-widget-assets/"
MIME_TYPE = "text/html+skybridge"

mcp = FastMCP(name="react-widget-mcp", stateless_http=True)


@mcp._mcp_server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="show-greeting-widget",
            title="Show Greeting React Widget",
            description="Render the widget",
            inputSchema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            },
            _meta={
                "openai/outputTemplate": WIDGET_URI,
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True
            }
        )
    ]


@mcp._mcp_server.list_resources()
async def list_resources():
    resources = [
        types.Resource(
            name="greeting-widget",
            title="Greeting Widget",
            uri=WIDGET_URI,
            mimeType=MIME_TYPE,
        )
    ]

    if DIST_WIDGET_DIR.exists():
        for f in DIST_WIDGET_DIR.rglob("*"):
            if f.is_file() and f.name != "index.html":
                rel = str(f.relative_to(DIST_WIDGET_DIR)).replace("\\", "/")
                uri = ASSETS_URI + rel
                resources.append(
                    types.Resource(
                        name=f"asset-{f.name}",
                        uri=uri,
                        mimeType="application/javascript" if f.suffix == ".js" else "text/css",
                        description="Widget asset"
                    )
                )
    return resources


def find_html():
    if DIST_WIDGET_DIR.exists():
        html_files = list(DIST_WIDGET_DIR.glob("*.html"))
        if html_files:
            return html_files[0]
    if DEV_WIDGET_HTML.exists():
        return DEV_WIDGET_HTML
    return None


async def read_resource(req: types.ReadResourceRequest):
    uri = str(req.params.uri)

    if uri == WIDGET_URI:
        html_file = find_html()
        if not html_file:
            return types.ServerResult(types.ReadResourceResult(contents=[]))

        html = html_file.read_text(encoding="utf8")

        html = html.replace(
            './assets/',
            ASSETS_URI + 'assets/'
        )

        return types.ServerResult(
            types.ReadResourceResult(
                contents=[
                    types.TextResourceContents(
                        uri=WIDGET_URI,
                        mimeType=MIME_TYPE,
                        text=html
                    )
                ]
            )
        )

    if uri.startswith(ASSETS_URI):
        rel = uri[len(ASSETS_URI):]
        file_path = DIST_WIDGET_DIR / rel

        if not file_path.exists():
            return types.ServerResult(types.ReadResourceResult(contents=[]))

        mime = (
            "application/javascript"
            if file_path.suffix == ".js"
            else "text/css"
        )

        return types.ServerResult(
            types.ReadResourceResult(
                contents=[
                    types.TextResourceContents(
                        uri=uri,
                        mimeType=mime,
                        text=file_path.read_text(encoding="utf8")
                    )
                ]
            )
        )

    return types.ServerResult(types.ReadResourceResult(contents=[]))


mcp._mcp_server.request_handlers[types.ReadResourceRequest] = read_resource


async def call_tool(req: types.CallToolRequest):
    args = req.params.arguments or {}
    name = args.get("name", "")
    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text="Widget Loaded!")],
            structuredContent={"name": name},
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)