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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)