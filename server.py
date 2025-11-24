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
                    "pizzaTopping": {"type": "string"},
                    "cheeseType": {"type": "string"},
                },
                "required": ["pizzaTopping", "cheeseType"],
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
    cheese = args.get("cheeseType", "")

    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Widget rendered!")],
            structuredContent={
                "pizzaTopping": topping,
                "cheeseType": cheese,
            },
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# from fastmcp import FastMCP
# import pathlib
#
# mcp = FastMCP("my-mcp-app")
#
# WIDGET_URI = "ui://widget/info-widget.html"
#
# widget_html = pathlib.Path("widget.html").read_text()
#
#
# @mcp.resource(WIDGET_URI)
# async def widget():
#     return {
#         "contents": [
#             {
#                 "uri": WIDGET_URI,
#                 "mimeType": "text/html+skybridge",
#                 "text": widget_html,
#             }
#         ]
#     }
#
#
# @mcp.tool(
#     meta={
#         "openai/outputTemplate": WIDGET_URI,           # <— CRITICAL
#         "openai/widgetAccessible": True,
#         "openai/resultCanProduceWidget": True,
#     }
# )
# async def get_info(topic: str):
#     return {
#         "structuredContent": {"topic": topic},
#         "content": [{"type": "text", "text": f"Topic is {topic}"}],
#         "_meta": {"echo": topic},
#     }
#
#
# if __name__ == "__main__":
#     mcp.run(
#         transport="http",
#         host="127.0.0.1",
#         port=8000,
#         path="/mcp"
#     )


# from fastmcp import FastMCP
# import pathlib
# import datetime
#
# mcp = FastMCP(name="example")
#
# widget_html = """
# <!DOCTYPE html>
# <html>
# <head>
#   <script src="https://cdn.jsdelivr.net/npm/@openai/skybridge@latest/dist/skybridge.js"></script>
# </head>
# <body>
#   <h1>Widget Loaded</h1>
#   <pre id="output"></pre>
#
#   <script>
#     const mcp = new window.Skybridge.MCP();
#     mcp.on("toolData", data => {
#       document.getElementById("output").textContent = JSON.stringify(data, null, 2);
#     });
#   </script>
# </body>
# </html>
# """
#
# WIDGET_URI = "ui://widget/info-widget.html"
#
#
# @mcp.resource(WIDGET_URI)
# async def widget_resource():
#     return {
#         "contents": [
#             {
#                 "uri": WIDGET_URI,
#                 "mimeType": "text/html+skybridge",
#                 "text": widget_html,
#             }
#         ]
#     }
#
#
# @mcp.tool(
#     meta={"openai/outputTemplate": WIDGET_URI}
# )
# async def get_info(topic: str):
#     return {
#         "structuredContent": {"topic": topic, "summary": f"Summary about {topic}"},
#         "content": [{"type": "text", "text": f"Info on {topic}"}],
#         # "_meta": {"timestamp": datetime.datetime.utcnow().isoformat()},
#     }
#
#
# if __name__ == "__main__":
#     mcp.run(transport="http",host="0.0.0.0", port=8000, path="/mcp")


# from fastmcp import FastMCP
# import pathlib
# import datetime
#
# # Create MCP server
# mcp = FastMCP(name="my-mcp-app")
#
# widget_path = pathlib.Path("web/dist/widget.html")
# widget_html = widget_path.read_text(encoding="utf-8")
# print(f"Loaded widget HTML, length={len(widget_html)}")
#
#
# @mcp.resource("ui://test/hello.html")
# async def hello():
#     return {
#         "contents": [
#             {
#                 "uri": "ui://test/hello.html",
#                 "mimeType": "text/html",
#                 "text": "<html><body><h1>Hello from MCP resource!</h1></body></html>"
#             }
#         ]
#     }
#
#
# @mcp.resource("ui://widget/widget.html")
# async def widget_template():
#     return {
#         "contents": [
#             {
#                 "uri": "ui://widget/widget.html",
#                 "mimeType": "text/html+skybridge",
#                 "text": widget_html,
#                 "_meta": {
#                     "openai/widgetPrefersBorder": True,
#                 },
#             }
#         ]
#     }
#
#
# @mcp.tool(
#     meta={
#         "openai/outputTemplate": "ui://widget/widget.html",
#     }
# )
# async def get_info(topic: str) -> dict:
#     timestamp = datetime.datetime.utcnow().isoformat()
#
#     return {
#         "structuredContent": {
#             "topic": topic,
#             "summary": f"Summary about {topic}",
#         },
#         "content": [
#             {
#                 "type": "text",
#                 "text": "Generated at `{timestamp}` for {topic}"
#             }
#         ],
#         "_meta": {
#             "serverTimestamp": timestamp,
#             "echo": topic,
#         },
#     }
#
#
# if __name__ == "__main__":
#     mcp.run(
#         transport="http",
#         host="0.0.0.0",
#         port=8000,
#         path="/mcp"
#     )


# from fastmcp import FastMCP
# import pathlib
# import datetime
#
# # Create MCP server
# mcp = FastMCP(name="my-mcp-app")
#
# widget_path = pathlib.Path("web/dist/widget.html")
# widget_html = widget_path.read_text(encoding="utf-8")
# print(f"Loaded widget HTML, length={len(widget_html)}")
#
#
# @mcp.resource("ui://test/hello.html")
# async def hello():
#     return {
#         "contents": [
#             {
#                 "uri": "ui://test/hello.html",
#                 "mimeType": "text/html",
#                 "text": "<html><body><h1>Hello from MCP resource!</h1></body></html>"
#             }
#         ]
#     }
#
#
# @mcp.resource("ui://widget/info-widget.html")
# async def widget_template():
#     return {
#         "contents": [
#             {
#                 "uri": "ui://widget/info-widget.html",
#                 "mimeType": "text/html+skybridge",
#                 "text": widget_html,
#                 "_meta": {
#                     "openai/widgetPrefersBorder": True,
#                 },
#             }
#         ]
#     }
#
#
# @mcp.tool
# async def get_info(topic: str) -> dict:
#     timestamp = datetime.datetime.utcnow().isoformat()
#
#     structured = {
#         "topic": topic,
#         "summary": f"This is a generated summary about {topic}.",
#     }
#
#     content = [
#         {
#             "type": "text",
#             "text": f"Here is information about **{topic}**. I generated this at `{timestamp}`."
#         }
#     ]
#
#     meta = {
#         "serverTimestamp": timestamp,
#         "echo": topic,
#         "extraDetails": {
#             "length": len(topic),
#             "uppercase": topic.upper(),
#         }
#     }
#
#     return {
#         "structuredContent": structured,
#         "content": content,
#         "_meta": {
#             "serverTimestamp": timestamp,
#             "echo": topic,
#             "extraDetails": {
#                 "length": len(topic),
#                 "uppercase": topic.upper(),
#             },
#             "openai/outputTemplate": "ui://widget/info-widget.html",
#         },
#     }
#
#
# if __name__ == "__main__":
#     mcp.run(
#         transport="http",
#         host="0.0.0.0",
#         port=8000,
#         path="/mcp"
#     )
