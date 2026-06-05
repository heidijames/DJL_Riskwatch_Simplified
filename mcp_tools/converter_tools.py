# Conversion logic and HTTP endpoints are defined here so they can be reused
# by both the FastAPI app and the MCP tool registrations.

# RiskWatch tools and HTTP endpoints are defined here so they can be reused
# by both the FastAPI app and the MCP tool registrations.

from datetime import date
from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from mcp_resources.converter_resources import (
    shipment_history,
    shipping_line_updates,
)

router = APIRouter(prefix="", tags=["riskwatch"])

#-------- Risk Assessment Logic --------------------------------
CARGO_RISK_SCORES = {
    "general": 10,
    "temp": 30,
    "critical": 50,
}

#---------- Request Models -----------------------------------

class RouteRiskRequest(BaseModel):
    shipment_id: str = Field(min_length=1)
    planned_dispatch_date: date
    origin_port: str
    destination_port: str
    cargo_type: str

    @field_validator("origin_port", "destination_port")
    @classmethod
    def validate_port(cls, value):
        supported_ports = shipment_history()["supported_ports"]

        for port in supported_ports:
            if port.lower() == value.lower():
                return port

        raise ValueError(f"Unsupported port: {value}")

    @field_validator("cargo_type")
    @classmethod
    def validate_cargo(cls, value):
        cargo_type = value.lower()

        if cargo_type not in CARGO_RISK_SCORES:
            raise ValueError(f"Unsupported cargo type: {value}")

        return cargo_type


class ShippingLineUpdateRequest(BaseModel):
    shipment_id: str = Field(min_length=1)

    @field_validator("shipment_id")
    @classmethod
    def validate_shipment_id(cls, value):
        return value.strip().upper()


#-------- Helper Function -------------------------------------
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


#-------Core Business Logic Functions

def assess_route_risk_value(
    shipment_id: str,
    planned_dispatch_date: date,
    origin_port: str,
    destination_port: str,
    cargo_type: str,
):
    """
    Assess shipment route risk before dispatch.
    """

    shipment_data = shipment_history()
    port_risk_scores = shipment_data["port_risk_scores"]

    port_risk = port_risk_scores.get(
        destination_port,
        10,
    )

    cargo_risk = CARGO_RISK_SCORES[
        cargo_type
    ]

    risk_score = port_risk + cargo_risk
    risk_level = get_risk_level(risk_score)

    return {
        "shipment_id": shipment_id,
        "planned_dispatch_date": str(planned_dispatch_date),
        "origin_port": origin_port,
        "destination_port": destination_port,
        "cargo_type": cargo_type,
        "port_risk_score": port_risk,
        "cargo_risk_score": cargo_risk,
        "risk_score": risk_score,
        "risk_level": risk_level,
    }


def get_shipping_line_update_value(
    shipment_id: str,
):
    """
    Retrieve the latest shipping line update for a shipment.
    """

    update_data = shipping_line_updates()
    updates = update_data["updates"]

    shipment_id = shipment_id.strip().upper()

    if shipment_id not in updates:
        return {
            "error": f"No shipping line update found for {shipment_id}"
        }

    update = updates[shipment_id]

    return {
        "shipment_id": shipment_id,
        "shipping_line": update.get("shipping_line"),
        "current_status": update.get("current_status"),
        "current_location": update.get("current_location"),
        "eta": update.get("eta"),
        "delay_days": update.get("delay_days"),
        "update_note": update.get("update_note"),
    }



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
