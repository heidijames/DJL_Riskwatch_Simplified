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

    shipment_id = shipment_id.strip().upper()
    origin_port = origin_port.strip()
    destination_port = destination_port.strip()
    cargo_type = cargo_type.strip().lower()

    shipment_data = shipment_history()
    supported_ports = shipment_data["supported_ports"]

    origin_match = None
    destination_match = None

    for port in supported_ports:

        if port.lower() == origin_port.lower():
            origin_match = port

        if port.lower() == destination_port.lower():
            destination_match = port

    if origin_match is None:
        return {
            "error": f"Unsupported origin port: {origin_port}"
        }

    if destination_match is None:
        return {
            "error": f"Unsupported destination port: {destination_port}"
        }

    origin_port = origin_match
    destination_port = destination_match

    port_risk_scores = shipment_data["port_risk_scores"]

    port_risk = port_risk_scores.get(
        destination_port,
        10,
    )

    cargo_risk = CARGO_RISK_SCORES.get(
        cargo_type
    )

    if cargo_risk is None:
        return {
            "error": f"Unsupported cargo type: {cargo_type}"
        }

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


# --- FastAPI Endpoints -------------------------------------------------------

@router.post("/assess-route-risk")
def assess_route_risk(request: RouteRiskRequest):
    """
    HTTP endpoint: assess shipment route risk.
    """

    return assess_route_risk_value(
        request.shipment_id,
        request.planned_dispatch_date,
        request.origin_port,
        request.destination_port,
        request.cargo_type,
    )


@router.post("/shipping-line-update")
def get_shipping_line_update(request: ShippingLineUpdateRequest):
    """
    HTTP endpoint: retrieve latest shipping line update.
    """

    return get_shipping_line_update_value(
        request.shipment_id
    )

# --- Metadata for MCP tool registration ----

TOOL_DEFINITIONS = [
    {
        "name": "assess_route_risk",
        "description": "Assess shipment route risk before dispatch.",
        "func": assess_route_risk_value,
        "tags": {"risk", "shipment", "logistics"},
    },
    {
        "name": "get_shipping_line_update",
        "description": "Retrieve the latest shipping line update for a shipment.",
        "func": get_shipping_line_update_value,
        "tags": {"shipment", "shipping-line", "status"},
    },
]


