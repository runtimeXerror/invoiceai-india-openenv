"""
InvoiceAI India — HTTP Client for the Invoice Extraction Environment.
"""

import requests
from typing import Optional
from models import InvoiceAction, InvoiceObservation, InvoiceState


class InvoiceEnvClient:
    """Simple HTTP client for the InvoiceAI environment."""

    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict:
        resp = requests.get(f"{self.base_url}/health", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def reset(self, task_id: str = "easy") -> dict:
        resp = requests.post(
            f"{self.base_url}/reset",
            json={"task_id": task_id},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def step(self, action: InvoiceAction) -> dict:
        resp = requests.post(
            f"{self.base_url}/step",
            json=action.model_dump(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def state(self) -> dict:
        resp = requests.get(f"{self.base_url}/state", timeout=10)
        resp.raise_for_status()
        return resp.json()
