from fastmcp import FastMCP
import pathlib
import datetime

mcp = FastMCP(name="example")

widget_html = """
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/@openai/skybridge@latest/dist/skybridge.js"></script>
</head>
<body>
  <h1>Widget Loaded</h1>
  <pre id="output"></pre>

  <script>
    const mcp = new window.Skybridge.MCP();
    mcp.on("toolData", data => {
      document.getElementById("output").textContent = JSON.stringify(data, null, 2);
    });
  </script>
</body>
</html>
"""


@mcp.resource("ui://widget/info-widget.html")
async def widget_resource():
    return {
        "contents": [
            {
                "uri": "ui://widget/info-widget.html",
                "mimeType": "text/html+skybridge",
                "text": widget_html,
            }
        ]
    }


@mcp.tool(
    meta={"openai/outputTemplate": "ui://widget/info-widget.html"}
)
async def get_info(topic: str):
    return {
        "structuredContent": {"topic": topic, "summary": f"Summary about {topic}"},
        "content": [{"type": "text", "text": f"Info on {topic}"}],
        "_meta": {"timestamp": datetime.datetime.utcnow().isoformat()},
    }


if __name__ == "__main__":
    mcp.run(transport="http",host="0.0.0.0", port=8000, path="/mcp")

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
