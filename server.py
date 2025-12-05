from pathlib import Path
import mcp.types as types
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent

DIST_DIR = ROOT / "dist" / "widgets" / "greeting-widget"
DEV_HTML = ROOT / "widgets" / "greeting-widget" / "index.html"
WIDGET_URI = "ui://widget/greeting-widget.html"
MIME_TYPE = "text/html+skybridge"

mcp = FastMCP(name="minimal-react-widget", stateless_http=True)


@mcp._mcp_server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="show-greeting-widg    et",
            title="Show Greeting React Widget",
            description="Displays the greeting widget",
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
            uri=WIDGET_URI,
            mimeType=MIME_TYPE,
            description="Greeting widget HTML",
        )
    ]


import re


def load_html():
    if DIST_DIR.exists():
        html_files = list(DIST_DIR.glob("*.html"))
        if html_files:
            html_path = html_files[0]
            html = html_path.read_text(encoding="utf8")

            # Inline JS and CSS assets as before
            for asset in DIST_DIR.rglob("*.js"):
                js_text = asset.read_text(encoding="utf8")
                js_path = f'./assets/{asset.name}'
                script_tag = f'<script type="module" crossorigin src="{js_path}"></script>'
                inline_script_tag = f'<script type="module">{js_text}</script>'
                if script_tag in html:
                    html = html.replace(script_tag, inline_script_tag)

            for asset in DIST_DIR.rglob("*.css"):
                css_text = asset.read_text(encoding="utf8")
                css_path = f'./assets/{asset.name}'
                link_tag = f'<link rel="stylesheet" href="{css_path}">'
                inline_style_tag = f'<style>{css_text}</style>'
                if link_tag in html:
                    html = html.replace(link_tag, inline_style_tag)

            # Extract all <script> tags from <head>
            head_scripts = re.findall(r'(<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>)', html.split('</head>')[0],
                                      flags=re.DOTALL)
            # Remove them from head
            html = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html, flags=re.DOTALL)

            # Find <div id="root"></div> position
            match = re.search(r'(<div\s+id=["\']root["\']\s*>\s*<\/div>)', html)
            if match:
                insert_pos = match.end()
                # Insert scripts after the root div
                html = html[:insert_pos] + ''.join(head_scripts) + html[insert_pos:]
            else:
                # fallback: insert scripts before </body>
                html = html.replace("</body>", ''.join(head_scripts) + "</body>")

            return html

    if DEV_HTML.exists():
        return DEV_HTML.read_text(encoding="utf8")

    return "<html><body>Widget not found</body></html>"


async def read_resource(req: types.ReadResourceRequest):
    if str(req.params.uri) != WIDGET_URI:
        return types.ServerResult(types.ReadResourceResult(contents=[]))

    html = load_html()

    return types.ServerResult(
        types.ReadResourceResult(
            contents=[
                types.TextResourceContents(
                    uri=WIDGET_URI,
                    mimeType=MIME_TYPE,
                    text=html,
                )
            ]
        )
    )


mcp._mcp_server.request_handlers[types.ReadResourceRequest] = read_resource


async def call_tool(req: types.CallToolRequest):
    args = req.params.arguments or {}
    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text="Widget Loaded!")],
            structuredContent=args,
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
