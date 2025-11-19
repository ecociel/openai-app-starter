from fastmcp import FastMCP
import pathlib
import datetime

# Create MCP server
mcp = FastMCP(name="my-mcp-app")

widget_path = pathlib.Path("web/dist/widget.html")
widget_html = widget_path.read_text(encoding="utf-8")
print(f"Loaded widget HTML, length={len(widget_html)}")


@mcp.resource("ui://test/hello.html")
async def hello():
    return {
        "contents": [
            {
                "uri": "ui://test/hello.html",
                "mimeType": "text/html",
                "text": "<html><body><h1>Hello from MCP resource!</h1></body></html>"
            }
        ]
    }


@mcp.resource("ui://widget/info-widget.html")
async def widget_template():
    return {
        "contents": [
            {
                "uri": "ui://widget/info-widget.html",
                "mimeType": "text/html+skybridge",
                "text": widget_html,
                "_meta": {
                    "openai/widgetPrefersBorder": True,
                },
            }
        ]
    }


@mcp.tool
async def get_info(topic: str) -> dict:
    timestamp = datetime.datetime.utcnow().isoformat()

    structured = {
        "topic": topic,
        "summary": f"This is a generated summary about {topic}.",
    }

    content = [
        {
            "type": "text",
            "text": f"Here is information about **{topic}**. I generated this at `{timestamp}`."
        }
    ]

    meta = {
        "serverTimestamp": timestamp,
        "echo": topic,
        "extraDetails": {
            "length": len(topic),
            "uppercase": topic.upper(),
        }
    }

    return {
        "structuredContent": structured,
        "content": content,
        "_meta": {
            "serverTimestamp": timestamp,
            "echo": topic,
            "extraDetails": {
                "length": len(topic),
                "uppercase": topic.upper(),
            },
            "openai/outputTemplate": "ui://widget/info-widget.html",
        },
    }


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        path="/mcp"
    )


# import datetime
# from fastmcp import FastMCP
# from mcp.types import EmbeddedResource
#
# server = FastMCP(name="widget-mcp-server")
#
#
# @server.resource("ui://widget/{name}.html")
# def serve_widget(name, req=None):
#     html = """
#     <!DOCTYPE html>
#     <html>
#       <body>
#         <h1>Widget Loaded!</h1>
#         <p>This confirms the widget is working.</p>
#       </body>
#     </html>
#     """
#
#     return {
#         "contents": [
#             EmbeddedResource(
#                 uri=f"ui://widget/{name}.html",
#                 mimeType="text/html+skybridge",
#                 text=html,
#             )
#         ]
#     }
#
#
# @server.tool()
# def get_info(topic: str):
#
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
#                 "text": f"Info about **{topic}** generated at `{timestamp}`."
#             }
#         ],
#         "_meta": {
#             "openai/outputTemplate": "ui://widget/info-widget.html",
#             "serverTimestamp": timestamp,
#         },
#     }
#
#
# if __name__ == "__main__":
#     server.run(
#         transport="http",
#         host="0.0.0.0",
#         port=8000,
#         path="/mcp"
#     )


# from fastmcp import FastMCP
# import pathlib
# import datetime
#
# mcp = FastMCP(name="mcp-widget-demo")
#
# widget_html = "<html><body><h1>Hello Widget</h1></body></html>"
#
# @mcp.resource("ui://widget/info-widget.html", allow_any_uri=True)
# def widget_template():
#     return {
#         "contents": [
#             {
#                 "uri": "ui://widget/info-widget.html",
#                 "mimeType": "text/html+skybridge",
#                 "text": widget_html,
#             }
#         ]
#     }
#
# # @mcp.resource("ui://widget/info-widget.html")
# # def widget():
# #     return {
# #         "contents": [
# #             {
# #                 "uri": "ui://widget/info-widget.html",
# #                 "mimeType": "text/html+skybridge",
# #                 "text": widget_html,
# #             }
# #         ]
# #     }
#
# @mcp.tool
# def get_info(topic: str) -> dict:
#     timestamp = datetime.datetime.utcnow().isoformat()
#     return {
#         "structuredContent": {
#             "topic": topic,
#             "summary": f"Summary about {topic}",
#         },
#         "content": [
#             {
#                 "type": "text",
#                 "text": f"Info about **{topic}** generated at `{timestamp}`"
#             }
#         ],
#         "_meta": {
#             "openai/outputTemplate": "ui://widget/info-widget.html",
#             "serverTimestamp": timestamp,
#             "openai/widgetAccessible": "true"
#         },
#     }
#
# if __name__ == "__main__":
#     print("Registered resources:", mcp.server.resources)
#     mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")
