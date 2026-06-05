"""Prompt templates used by the unit converter tutorial."""

from __future__ import annotations

from typing import List, Dict


def risk_assessment_summary_prompt() -> List[Dict[str, str]]:
    """
    Generate a risk assessment summary.
    """

    return [
        {
            "role": "system",
            "content": (
                "You are a logistics risk analyst. "
                "Explain shipment risk in simple business language. "
                "Summarize the risk score, risk level, and operational implications. "
                "Keep the response concise and practical."
            ),
        },
        {
            "role": "user",
            "content": (
                "Explain the shipment risk assessment for shipment "
                "{shipment_id} travelling from {origin_port} "
                "to {destination_port} carrying {cargo_type}. "
                "The risk score is {risk_score} and the risk level is {risk_level}."
            ),
        },
    ]



def shipping_line_status_prompt() -> List[Dict[str, str]]:
    """
    Generate a shipment status summary.
    """

    return [
        {
            "role": "system",
            "content": (
                "You are a logistics coordinator. "
                "Summarize shipment status updates clearly and professionally. "
                "Highlight delays, ETA changes, and operational concerns."
            ),
        },
        {
            "role": "user",
            "content": (
                "Summarize the latest shipment update. "
                "Shipment ID: {shipment_id}. "
                "Current Status: {current_status}. "
                "Current Location: {current_location}. "
                "ETA: {eta}. "
                "Delay Days: {delay_days}."
            ),
        },
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

