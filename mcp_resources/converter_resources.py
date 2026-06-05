"""Reusable MCP resources for the unit converter tutorial."""

from __future__ import annotations

from typing import Any, Dict

# Read CSV and JSON files
import csv
import json

# File path handling
from pathlib import Path

# File Locations
BASE_DIR = Path(__file__).parent

SHIPMENT_DATA_FILE = BASE_DIR / "global_supply_chain_risk_2026.csv"

SHIPPING_LINE_FILE = BASE_DIR / "shipping_line_updates.json"


# Configuration

SUPPORTED_PORTS = [
    "Singapore",
    "Port Klang",
    "Shanghai",
    "Dubai",
]


### Helper Functions

def load_csv(file_path):
    """
    Load shipment history data from a CSV file.

    Returns:
        List of shipment records.
    """

    rows = []

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)

    return rows

shipment_history_data = load_csv(SHIPMENT_DATA_FILE)


def load_json(file_path):
    """
    Load shipping line update data from a JSON file.

    Returns:
        Dictionary containing shipment updates.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
    
shipping_line_update_data = load_json(SHIPPING_LINE_FILE)

def filter_supported_ports(shipments):
    """
    Keep only records involving the 4 supported ports:
    Singapore, Port Klang, Shanghai, and Dubai.

    Returns:
        Filtered shipment records.
    """

    filtered_shipments = []

    for shipment in shipments:

        if (
            shipment["Origin_Port"] in SUPPORTED_PORTS
            and shipment["Destination_Port"] in SUPPORTED_PORTS
        ):
            filtered_shipments.append(shipment)

    return filtered_shipments

shipment_history_data = filter_supported_ports(
    shipment_history_data
)



def calculate_port_risk(shipments):
    """
    Derive port risk scores from historical shipment records.

    The score is based on:
    - disruption rate
    - average carrier reliability
    - average lead time

    Returns:
        Dictionary containing destination ports and risk scores.
    """

    port_totals = {}

    for shipment in shipments:
        destination = shipment["Destination_Port"]

        reliability = float(shipment.get("Carrier_Reliability_Score", 0))
        lead_time = float(shipment.get("Lead_Time_Days", 0))
        disruption = int(shipment.get("Disruption_Occurred", 0))

        if destination not in port_totals:
            port_totals[destination] = {
                "count": 0,
                "reliability_total": 0,
                "lead_time_total": 0,
                "disruption_total": 0,
            }

        port_totals[destination]["count"] += 1
        port_totals[destination]["reliability_total"] += reliability
        port_totals[destination]["lead_time_total"] += lead_time
        port_totals[destination]["disruption_total"] += disruption

    port_risk_scores = {}

    for port, totals in port_totals.items():
        count = totals["count"]

        average_reliability = totals["reliability_total"] / count
        average_lead_time = totals["lead_time_total"] / count
        disruption_rate = totals["disruption_total"] / count

        if disruption_rate >= 0.50 or average_reliability < 0.60:
            risk_score = 30

        elif disruption_rate >= 0.25 or average_lead_time >= 20:
            risk_score = 20

        else:
            risk_score = 10

        port_risk_scores[port] = risk_score

    return port_risk_scores

port_risk_scores = calculate_port_risk(shipment_history_data)

# Resource Functions

def shipment_history() -> Dict[str, Any]:
    """
    Provides historical shipment records and derived port risk information.

    Returns:
        Dictionary containing supported ports, shipment records,
        and derived port risk scores.
    """

    return {
        "id": "shipment-history",
        "title": "Historical Shipment Records",
        "supported_ports": SUPPORTED_PORTS,
        "port_risk_scores": port_risk_scores,
        "records": shipment_history_data,
    }

def shipping_line_updates() -> Dict[str, Any]:
    """
    Provides current shipping line updates and information.

    Returns:
        Dictionary containing shipment status, location,
        estimated arrival dates, and delay information.
    """

    return {
        "id": "shipping-line-updates",
        "title": "Shipping Line Updates",
        "updates": shipping_line_update_data,
    }

# How would we scope this?
RESOURCE_DEFINITIONS = [
    {
        "name": "shipment_history",
        "description": "Filtered shipment history and derived port risk scores.",
        "mime_type": "application/json",
        "func": shipment_history,
    },
    {
        "name": "shipping_line_updates",
        "description": "Current shipment status updates from shipping lines.",
        "mime_type": "application/json",
        "func": shipping_line_updates,
    },
]



