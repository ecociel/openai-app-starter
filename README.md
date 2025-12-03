# mcp-app-python

**mcp-app-python** — Example MCP server in Python with HTML widget support.

## Overview

This project demonstrates how to build a Python-based MCP server that can serve plain HTML widgets to MCP-aware clients (e.g. LLM front-ends, inspectors, or custom UI).  

With this server, you can:  

- Expose standard MCP tools / resources.  
- Return not just text or JSON, but full HTML UIs (widgets) — e.g. forms, info boxes, interactive elements.  
- Organize widget HTML (and associated assets) in a dedicated directory structure, making it easier to manage multiple widgets.

---

## 🧠 What is MCP?

MCP (Model Context Protocol) is a standard for letting AI models access external tools, information, and UI components in a secure, structured way. MCP servers provide:

- **Tools**: Functions called by AI for executing logic.
- **Resources**: Data sources made available to the AI.
- **Widgets**: HTML or UI components that can be shown inside AI interfaces.

For more details, visit https://modelcontextprotocol.io
https://developers.openai.com/apps-sdk/quickstart
https://developers.openai.com/apps-sdk/build/mcp-server#structure-the-data-your-tool-returns

---

## 🧪 Getting Started

## Requirements

- Python 3.x (tested with 3.13)  
- `mcp` / `fastmcp` — e.g. `fastmcp 2.13.1`, `mcp 1.21.2`  
- (Optional) Node.js + npm — for using the MCP Inspector or other JS-based front-ends.  

### Install Requirements

```bash
python3 -m venv .venv
source .venv/bin/activate

git clone https://github.com/ecociel/mcp-app-python.git
cd mcp-app-python
pip install -r requirements.txt

