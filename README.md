# DJL RiskWatch API + MCP Server

DJL RiskWatch is a logistics risk assessment system built using FastAPI and FastMCP.

- builds the FastAPI app, wraps it with FastMCP, mounts MCP HTTP/SSE endpoints, registers resources and prompts, and starts uvicorn.
- requirements.txt – Python dependencies.

The system provides:

• Route risk assessment before shipment dispatch
• Shipping line status monitoring
• MCP resources for shipment history and shipping updates
• MCP prompts for business summaries and shipment reporting


## Prerequisites

- Python 3.10+ (tested with 3.12).
- Virtual environment.
- npm inspector below.

⸻

## Setup from this folder

```bash
python -m venv .venv

# Mac or Gitbash
source .venv/bin/activate
 

# Windows powershell:
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

⸻

## Run the HTTP + MCP server

```bash
# start the server
python converter_streamable_http_server.py

# or
python -m converter_streamable_http_server

```

You’ll see:

- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

MCP endpoints served by FastMCP:

- streamable-http: http://localhost:8003/mcp
- SSE: http://localhost:8003/sse

⸻

## System Components

Tools
  assess_route_risk
  get_shipping_line_update

Resources
  resource://shipment_history
  resource://shipping_line_updates

Prompts
  risk_assessment_summary
  shipping_line_status_summary

⸻

## Supported Inputs

# Supported Ports
  Singapore
  Port Klang
  Shanghai
  Dubai

# Cargo Types
  general
  temp
  critical

# Shipment ID Format
  Shipment IDs must follow this format:

  SHP001

## Try the HTTP endpoints (curl)

1. Assess Route Risk - Valid Input
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
2. Assess Route Risk - Invalid Shipment ID
```bash
curl -X POST "http://localhost:8003/assess-route-risk" \
-H "Content-Type: application/json" \
-d '{
  "shipment_id":"BANANA",
  "planned_dispatch_date":"2026-06-15",
  "origin_port":"Singapore",
  "destination_port":"Shanghai",
  "cargo_type":"temp"
}'

Expected result:

422 Validation Error
```

3. Assess Route Risk - Invalid Port
```bash
curl -X POST "http://localhost:8003/assess-route-risk" \
-H "Content-Type: application/json" \
-d '{
  "shipment_id":"SHP001",
  "planned_dispatch_date":"2026-06-15",
  "origin_port":"Perth",
  "destination_port":"Shanghai",
  "cargo_type":"temp"
}'

Expected result:

Validation error or unsupported port error
```

4. Shipping Line Update - Valid Shipment ID
```bash
curl -X POST "http://localhost:8003/shipping-line-update" \
-H "Content-Type: application/json" \
-d '{
  "shipment_id":"SHP001"
}'
```
5. Shipping Line Update - Unknown Shipment ID
```bash
curl -X POST "http://localhost:8003/shipping-line-update" \
-H "Content-Type: application/json" \
-d '{
  "shipment_id":"SHP999"
}'

Expected result:

404 Not Found
```
## Headers & Authentication (common to all)

### Add JSON content type (and optionally your auth token)

-H "Content-Type: application/json" \
-H "Authorization: Bearer <TOKEN>"

Our server doesn’t require auth yet, we can omit the **Authorization** header.

## Inspect with MCP Inspector

# Streamable HTTP
npx @modelcontextprotocol/inspector@latest -e DUMMY=1 --url http://localhost:8003/mcp --transport streamable-http

# STDIO
npx @modelcontextprotocol/inspector python converter_stdio_server.py

In MCP Inspector, verify:

Tools:
  assess_route_risk
  get_shipping_line_update
Resources:
  shipment_history
  shipping_line_updates
Prompts:
  risk_assessment_summary
  shipping_line_status_summary

## MCP JSON-RPC Examples

# List Tools
curl -s -X POST "http://localhost:8003/mcp" \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'

# List Resources
curl -s -X POST "http://localhost:8003/mcp" \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"resources/list","params":{},"id":2}'

# Read Shipment History Resource
curl -s -X POST "http://localhost:8003/mcp" \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"resources/read","params":{"uri":"resource://shipment_history"},"id":3}'

# Read Shipping Line Updates Resource
curl -s -X POST "http://localhost:8003/mcp" \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"resources/read","params":{"uri":"resource://shipping_line_updates"},"id":4}'

# List Prompts
curl -s -X POST "http://localhost:8003/mcp" \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"prompts/list","params":{},"id":5}'
# Get Risk Assessment Prompt
curl -s -X POST "http://localhost:8003/mcp" \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"prompts/get","params":{"name":"risk_assessment_summary"},"id":6}'

## Project Structure
DJL_Riskwatch_Simplified/
│
├── converter_streamable_http_server.py
├── converter_stdio_server.py
├── requirements.txt
│
├── mcp_resources/
│   ├── converter_resources.py
│   ├── global_supply_chain_risk_2026.csv
│   └── shipping_line_updates.json
│
├── mcp_tools/
│   └── converter_tools.py
│
├── mcp_prompts/
│   └── converter_prompts.py
│
├── utils/
│   └── logging_utils.py
│
├── logs/
└── docs/

## Development Notes

This project was built from the lecturer’s FastAPI + MCP starter code.

The original unit converter logic was replaced with logistics-specific RiskWatch logic:

Resources were changed to shipment history and shipping line updates.

Tools were changed to route risk assessment and shipment status lookup.

Prompts were changed to business summaries for logistics use cases.

Validation was added using Pydantic and defensive checks inside core business logic.

## Testing was completed through:

Swagger / FastAPI
MCP Inspector
curl commands
Git version control


## Error Handling

# Common HTTP errors:

422 Validation Error - invalid request body or input format
404 Not Found - shipment ID not found in shipping update resource
400 Bad Request - unsupported business input, if handled by endpoint logic

# Common MCP JSON-RPC errors:

-32700 Parse error
-32600 Invalid request
-32601 Method not found
-32602 Invalid params
-32603 Internal error