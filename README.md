# DJL RiskWatch API + MCP Server

DJL RiskWatch is a logistics risk assessment system built using FastAPI and FastMCP.

The system provides:

* Shipment route risk assessment
* Shipping line status lookup
* MCP tools, resources, and prompts
* HTTP API endpoints through FastAPI
* MCP access through Streamable HTTP

---

## Prerequisites

* Python 3.10+
* Virtual environment
* npm (for MCP Inspector)

---

## Setup from this folder

```bash
python -m venv .venv

# Git Bash
source .venv/Scripts/activate

# Windows PowerShell
.venv\Scripts\activate

python -m pip install -r requirements.txt
```

---

## Run the HTTP + MCP Server

```bash
python converter_streamable_http_server.py
```

You should see:

```text
Swagger UI:
http://localhost:8003/docs

ReDoc:
http://localhost:8003/redoc

MCP Endpoint:
http://localhost:8003/mcp/

SSE Endpoint:
http://localhost:8003/sse
```

---

## Open MCP Inspector

With the server running, open a new terminal and run:

```bash
npx @modelcontextprotocol/inspector@latest \
-e DUMMY=1 \
--url http://localhost:8003/mcp/ \
--transport streamable-http
```

You should see:

```text
Proxy server listening...
Inspector running at:
http://localhost:6274
```

Open the displayed URL in your browser.

---

## MCP Components

### Tools

* assess_route_risk_assess_route_risk_post
* get_shipping_line_update_shipping_line_update_post

### Resources

* resource://shipment_history
* resource://shipping_line_updates

### Prompts

* risk_assessment_summary
* shipping_line_status

---

## Supported Inputs

### Shipment ID Format

```text
SHP001
SHP002
SHP123
```

### Supported Ports

* Singapore
* Shanghai
* Dubai
* Port Klang

### Supported Cargo Types

* general
* temp
* critical

---

## HTTP Endpoint Testing (curl)

### Assess Route Risk

```bash
curl -X POST "http://localhost:8003/assess-route-risk" \
-H "Content-Type: application/json" \
-d '{
  "shipment_id":"SHP001",
  "planned_dispatch_date":"2026-06-15",
  "origin_port":"Singapore",
  "destination_port":"Shanghai",
  "cargo_type":"temp"
}'
```

### Shipping Line Update

```bash
curl -X POST "http://localhost:8003/shipping-line-update" \
-H "Content-Type: application/json" \
-d '{
  "shipment_id":"SHP001"
}'
```

---

## Obtaining an MCP Session ID

The Streamable HTTP MCP endpoint requires a valid session ID before JSON-RPC requests can be executed.

Run:

```bash
curl -i http://localhost:8003/mcp/
```

Example response:

```text
HTTP/1.1 406 Not Acceptable

mcp-session-id: 141609fce5404d9f9f0e4aba4b2e4fee

{"jsonrpc":"2.0","error":{"message":"Client must accept text/event-stream"}}
```

Copy the value returned in:

```text
mcp-session-id
```

and use it in subsequent MCP JSON-RPC requests.

---

## MCP JSON-RPC Testing (curl)

### List Tools

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

### List Resources

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"resources/list","params":{},"id":2}'
```

### List Prompts

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"prompts/list","params":{},"id":3}'
```

### Get Risk Assessment Prompt

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"prompts/get","params":{"name":"risk_assessment_summary"},"id":4}'
```

### Get Shipping Line Status Prompt

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"prompts/get","params":{"name":"shipping_line_status"},"id":5}'
```

---

## MCP Inspector Testing

Use MCP Inspector to verify:

### Tools

* assess_route_risk_assess_route_risk_post
* get_shipping_line_update_shipping_line_update_post

### Resources

* shipment_history
* shipping_line_updates

### Prompts

* risk_assessment_summary
* shipping_line_status

---

## Project Structure

```text
DJL_Riskwatch_Simplified/

├── converter_streamable_http_server.py
├── converter_stdio_server.py
├── requirements.txt

├── mcp_tools/
│   └── converter_tools.py

├── mcp_resources/
│   ├── converter_resources.py
│   ├── global_supply_chain_risk_2026.csv
│   └── shipping_line_updates.json

├── mcp_prompts/
│   └── converter_prompts.py

├── utils/
│   └── logging_utils.py

├── logs/
└── README.md
```

---

## Error Handling

Common HTTP Errors:

* 400 Bad Request
* 404 Not Found
* 422 Validation Error

Common JSON-RPC Errors:

* -32700 Parse Error
* -32600 Invalid Request
* -32601 Method Not Found
* -32602 Invalid Parameters
* -32603 Internal Error

---

## Development Notes

Key issues discovered and resolved during testing:

1. Cargo type case sensitivity
2. Unsupported port validation
3. Shipment ID regex validation
4. MCP session ID requirement
5. Streamable HTTP MCP endpoint requires Accept headers and session-based communication

Testing was completed using:

* Swagger
* curl
* MCP Inspector
* Git version control

```
```
