import requests
import json

url = "http://localhost:8000/mcp"

payload = {
    "jsonrpc": "2.0",
    "method": "tool.invoke",
    "params": {
        "tool": "get_info",
        "input": {
            "topic": "chatgpt"
        }
    },
    "id": "1"
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json,text/event-stream",
    "MCP-Session": "test-session-123"
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.status_code)
print(response.text)