"""
InvoiceAI India — Typed models for the Invoice Data Extraction Environment.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ── Action ────────────────────────────────────────────────────────────────────
class InvoiceAction(BaseModel):
    """Agent's extraction attempt for a given invoice."""

    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None          # DD/MM/YYYY
    gstin: Optional[str] = None                 # 15-char GSTIN
    total_amount: Optional[float] = None
    subtotal: Optional[float] = None
    cgst: Optional[float] = None
    sgst: Optional[float] = None
    igst: Optional[float] = None
    line_items: Optional[List[Dict[str, Any]]] = None  # [{description, hsn, qty, rate, amount}]
    currency: Optional[str] = None              # INR, USD, etc.
    place_of_supply: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_gstin: Optional[str] = None


# ── Observation ───────────────────────────────────────────────────────────────
class InvoiceObservation(BaseModel):
    """What the agent sees each step."""

    invoice_text: str = ""                     # The raw invoice text to parse
    task_id: str = ""                           # easy / medium / hard
    task_description: str = ""
    fields_to_extract: List[str] = []           # Which fields are expected
    feedback: str = ""                          # Grader feedback from last step
    score: float = 0.0                          # Current cumulative score
    done: bool = False


# ── State ─────────────────────────────────────────────────────────────────────
class InvoiceState(BaseModel):
    """Episode metadata."""

    episode_id: Optional[str] = None
    step_count: int = 0
    task_id: str = ""
    max_steps: int = 5
    current_score: float = 0.0
    attempts: int = 0
