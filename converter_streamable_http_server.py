# DJL RiskWatch API + MCP (tools, resources, prompts)
# Uses FastAPI for HTTP routes and FastMCP to expose tools/resources/prompts over HTTP/SSE transports.

from fastapi import FastAPI, APIRouter
from fastmcp import FastMCP

from mcp_tools.converter_tools import router as converter_router

from mcp_resources.converter_resources import (
    shipment_history,
    shipping_line_updates,
)

from mcp_prompts.converter_prompts import (
    risk_assessment_summary_prompt,
    shipping_line_status_prompt,
)

from utils.logging_utils import build_log_config

import platform
import datetime
import os
import time
from pathlib import Path
import uvicorn

PORT = 8003

LOG_FILE = Path("logs/mcp_log_streamable_http.log")

LOG_CONFIG = build_log_config(
    LOG_FILE,
    logger_handlers={
        "uvicorn": ["rotating_file", "console"],
        "uvicorn.error": ["rotating_file", "console"],
        "uvicorn.access": ["rotating_file"],
    },
    root_level="INFO",
    logger_level="DEBUG",
)


app = FastAPI(
    title="DJL RiskWatch MCP Server",
    description="FastAPI endpoints exposed as MCP tools for shipment risk monitoring.",
    version="1.0.0",
)

app.include_router(converter_router)


system_router = APIRouter(prefix="", tags=["system"])
_started_at = time.time()


app.include_router(system_router)


mcp = FastMCP.from_fastapi(
    app,
    name="DJL RiskWatch MCP Server",
    instructions="Shipment risk assessment tools with supporting resources and prompts.",
)


# Resources

@mcp.resource(
    "resource://shipment_history",
    name="Shipment History",
    mime_type="application/json",
)
def _resource_shipment_history():
    return shipment_history()


@mcp.resource(
    "resource://shipping_line_updates",
    name="Shipping Line Updates",
    mime_type="application/json",
)
def _resource_shipping_line_updates():
    return shipping_line_updates()


# Prompts

@mcp.prompt(
    name="risk_assessment_summary",
    description="Generate a business summary of shipment risk.",
)
def _prompt_risk_assessment_summary():
    return risk_assessment_summary_prompt()


@mcp.prompt(
    name="shipping_line_status_summary",
    description="Generate a business summary of shipment status updates.",
)
def _prompt_shipping_line_status_summary():
    return shipping_line_status_prompt()


mcp_http_app = mcp.http_app(path="/", transport="streamable-http")
mcp_sse_app = mcp.http_app(path="/", transport="sse")

app.router.lifespan_context = mcp_http_app.lifespan

app.mount("/mcp", mcp_http_app)
app.mount("/sse", mcp_sse_app)


if __name__ == "__main__":
    print("Starting the DJL RiskWatch API server (HTTP + MCP tools/resources/prompts)...")
    print(f"HTTP docs:      http://localhost:{PORT}/docs")
    print(f"HTTP redoc:     http://localhost:{PORT}/redoc")
    print(f"MCP endpoint:   http://localhost:{PORT}/mcp (HTTP)")
    print(f"MCP endpoint:   http://localhost:{PORT}/sse (SSE)")

    uvicorn.run(
        app,
        host="localhost",
        port=PORT,
        log_level="trace",
        log_config=LOG_CONFIG,
    )