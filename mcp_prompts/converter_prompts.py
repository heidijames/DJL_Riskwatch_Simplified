"""Prompt templates used by the DJL RiskWatch system."""

from __future__ import annotations

from typing import List


def risk_assessment_summary_prompt() -> List[str]:
    """
    Generate a risk assessment summary.
    """

    return [
        (
            "You are a logistics risk analyst. "
            "Explain shipment risk in simple business language. "
            "Summarize the risk score, risk level, and operational implications. "
            "Keep the response concise and practical."
        ),
        (
            "Explain the shipment risk assessment for shipment "
            "{shipment_id} travelling from {origin_port} "
            "to {destination_port} carrying {cargo_type}. "
            "The risk score is {risk_score} and the risk level is {risk_level}."
        ),
    ]


def shipping_line_status_prompt() -> List[str]:
    """
    Generate a shipment status summary.
    """

    return [
        (
            "You are a logistics coordinator. "
            "Summarize shipment status updates clearly and professionally. "
            "Highlight delays, ETA changes, and operational concerns."
        ),
        (
            "Summarize the latest shipment update. "
            "Shipment ID: {shipment_id}. "
            "Current Status: {current_status}. "
            "Current Location: {current_location}. "
            "ETA: {eta}. "
            "Delay Days: {delay_days}."
        ),
    ]


PROMPT_DEFINITIONS = [
    {
        "name": "risk_assessment_summary",
        "description": "Generate a business summary of shipment risk.",
        "func": risk_assessment_summary_prompt,
    },
    {
        "name": "shipping_line_status_summary",
        "description": "Generate a business summary of shipment status updates.",
        "func": shipping_line_status_prompt,
    },
]