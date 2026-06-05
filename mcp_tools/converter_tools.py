# Conversion logic and HTTP endpoints are defined here so they can be reused
# by both the FastAPI app and the MCP tool registrations.

# RiskWatch tools and HTTP endpoints are defined here so they can be reused
# by both the FastAPI app and the MCP tool registrations.

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

from mcp_resources.converter_resources import (
    shipment_history,
    shipping_line_updates,
)

router = APIRouter(prefix="", tags=["riskwatch"])


#---------- Request Models -----------------------------------

class RouteRiskRequest(BaseModel):
    shipment_id: str
    planned_dispatch_date: str
    origin_port: str
    destination_port: str
    cargo_type: str


class ShippingLineUpdateRequest(BaseModel):
    shipment_id: str

#-------- Risk Assessment Logic --------------------------------
CARGO_RISK_SCORES = {
    "general": 10,
    "temp": 30,
    "critical": 50,
}

#-------- Helper Functions -------------------------------------
# Convert score to risk level
def get_risk_level(risk_score: int) -> str:
    """
    Convert a numerical risk score into a risk level.
    """

    if risk_score >= 70:
        return "High"

    elif risk_score >= 40:
        return "Medium"

    else:
        return "Low"

# Validation functions for input data

def validate_ports(origin_port: str, destination_port: str,
) -> dict | None:


    shipment_data = shipment_history()

    supported_ports = [
        port.lower()
        for port in shipment_data["supported_ports"]
    ]

    if origin_port.lower() not in supported_ports:
        return {
            "error":
            f"Unsupported origin port: {origin_port}"
        }

    if destination_port.lower() not in supported_ports:
        return {
            "error":
            f"Unsupported destination port: {destination_port}"
        }

    return None

  
def validate_cargo_type(cargo_type: str) -> dict | None:
    
    if cargo_type.lower() not in CARGO_RISK_SCORES:
        return {
            "error":
            f"Unsupported cargo type: {cargo_type}"
        }

    return None


def validate_shipment_id(shipment_id: str) -> dict | None:
   
    if not shipment_id:
        return {"error": "Shipment ID is required"}

    return None


def validate_dispatch_date(
    planned_dispatch_date: str
) -> dict | None:
    
    try:
        datetime.strptime(
            planned_dispatch_date,
            "%Y-%m-%d"
        )

    except ValueError:
        return {
            "error":
            "Date must use YYYY-MM-DD format"
        }

    return None








# --- FastAPI endpoints -------------------------------------------------------

@router.post("/celsius-to-fahrenheit")
def celsius_to_fahrenheit(celsius: float):
    """
    HTTP endpoint: convert Celsius to Fahrenheit.

    Args:
        celsius: Temperature in Celsius.

    Returns:
        JSON dict with the result and operation name.
    """
    result = celsius_to_fahrenheit_value(celsius)
    return {"result": result, "operation": "celsius_to_fahrenheit"}


@router.post("/fahrenheit-to-celsius")
def fahrenheit_to_celsius(fahrenheit: float):
    """
    HTTP endpoint: convert Fahrenheit to Celsius.

    Args:
        fahrenheit: Temperature in Fahrenheit.

    Returns:
        JSON dict with the result and operation name.
    """
    result = fahrenheit_to_celsius_value(fahrenheit)
    return {"result": result, "operation": "fahrenheit_to_celsius"}


@router.post("/kilometers-to-miles")
def kilometers_to_miles(kilometers: float):
    """
    HTTP endpoint: convert kilometers to miles.

    Args:
        kilometers: Distance in kilometers.

    Returns:
        JSON dict with the result and operation name.
    """
    result = kilometers_to_miles_value(kilometers)
    return {"result": result, "operation": "kilometers_to_miles"}


@router.post("/miles-to-kilometers")
def miles_to_kilometers(miles: float):
    """
    HTTP endpoint: convert miles to kilometers with input validation.

    Args:
        miles: Distance in miles.

    Returns:
        JSON dict with the result and operation name, or an error message.
    """
    try:
        result = miles_to_kilometers_value(miles)
        return {"result": result, "operation": "miles_to_kilometers"}
    except ValueError as exc:  # Keep HTTP response friendly
        return {"error": str(exc), "operation": "miles_to_kilometers"}


# --- Metadata for MCP tool registration ----

TOOL_DEFINITIONS = [
    {
        "name": "celsius_to_fahrenheit",
        "description": "Convert Celsius temperature to Fahrenheit",
        "func": celsius_to_fahrenheit_value,
        "tags": {"temperature", "conversion"},
    },
    {
        "name": "fahrenheit_to_celsius",
        "description": "Convert Fahrenheit temperature to Celsius",
        "func": fahrenheit_to_celsius_value,
        "tags": {"temperature", "conversion"},
    },
    {
        "name": "kilometers_to_miles",
        "description": "Convert kilometers to miles",
        "func": kilometers_to_miles_value,
        "tags": {"distance", "conversion"},
    },
    {
        "name": "miles_to_kilometers",
        "description": "Convert miles to kilometers (validates non‑negative input)",
        "func": miles_to_kilometers_value,
        "tags": {"distance", "conversion"},
    },
]
