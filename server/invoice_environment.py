"""
InvoiceAI India — Core Environment Logic
Implements step() / reset() / state() with graders for 3 tasks.
"""

import random
import uuid
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

from models import InvoiceAction, InvoiceObservation, InvoiceState

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.invoices import TASK_REGISTRY


def _normalize(val: Any) -> str:
    """Lowercase, strip whitespace for fuzzy matching."""
    if val is None:
        return ""
    return str(val).strip().lower().replace(",", "").replace("₹", "").replace("rs.", "").replace("rs", "")


def _string_similarity(a: str, b: str) -> float:
    """Return 0-1 similarity between two strings."""
    a_n, b_n = _normalize(a), _normalize(b)
    if not a_n and not b_n:
        return 1.0
    if not a_n or not b_n:
        return 0.0
    return SequenceMatcher(None, a_n, b_n).ratio()


def _numeric_closeness(predicted: Optional[float], expected: Optional[float], tolerance: float = 0.02) -> float:
    """Score numeric values — 1.0 if within tolerance%, partial otherwise."""
    if expected is None:
        return 1.0 if predicted is None else 0.0
    if predicted is None:
        return 0.0
    if expected == 0:
        return 1.0 if abs(predicted) < 1.0 else 0.0
    error = abs(predicted - expected) / abs(expected)
    if error <= tolerance:
        return 1.0
    elif error <= 0.1:
        return 0.5
    elif error <= 0.25:
        return 0.2
    return 0.0


def _grade_line_items(predicted: Optional[List[Dict]], expected: Optional[List[Dict]]) -> float:
    """Grade line items extraction — partial credit per item."""
    if expected is None:
        return 1.0 if predicted is None else 0.5
    if not predicted:
        return 0.0

    total_score = 0.0
    matched_indices = set()

    for exp_item in expected:
        best_score = 0.0
        best_idx = -1

        for idx, pred_item in enumerate(predicted):
            if idx in matched_indices:
                continue
            item_score = 0.0
            n_fields = 0

            # Description match
            if "description" in exp_item:
                item_score += _string_similarity(
                    pred_item.get("description", ""),
                    exp_item["description"]
                )
                n_fields += 1

            # HSN match
            if "hsn" in exp_item:
                item_score += _string_similarity(
                    str(pred_item.get("hsn", "")),
                    str(exp_item["hsn"])
                )
                n_fields += 1

            # Quantity match
            if "qty" in exp_item:
                try:
                    item_score += _numeric_closeness(float(pred_item.get("qty", 0)), float(exp_item["qty"]))
                except (ValueError, TypeError):
                    pass
                n_fields += 1

            # Amount match
            if "amount" in exp_item:
                try:
                    item_score += _numeric_closeness(float(pred_item.get("amount", 0)), float(exp_item["amount"]))
                except (ValueError, TypeError):
                    pass
                n_fields += 1

            avg = item_score / max(n_fields, 1)
            if avg > best_score:
                best_score = avg
                best_idx = idx

        if best_idx >= 0:
            matched_indices.add(best_idx)
        total_score += best_score

    return total_score / max(len(expected), 1)


def grade_extraction(action: InvoiceAction, ground_truth: Dict[str, Any], fields: List[str]) -> Tuple[float, str]:
    """
    Grade an extraction attempt against ground truth.
    Returns (score 0.0-1.0, feedback string).
    """
    field_scores: Dict[str, float] = {}

    for f in fields:
        expected = ground_truth.get(f)
        predicted = getattr(action, f, None)

        if f == "line_items":
            field_scores[f] = _grade_line_items(predicted, expected)
        elif f in ("total_amount", "subtotal", "cgst", "sgst", "igst"):
            field_scores[f] = _numeric_closeness(predicted, expected)
        elif f in ("vendor_name", "buyer_name", "place_of_supply", "currency"):
            field_scores[f] = _string_similarity(str(predicted or ""), str(expected or ""))
        else:
            # Exact or near-exact string match
            field_scores[f] = _string_similarity(str(predicted or ""), str(expected or ""))

    total = sum(field_scores.values()) / max(len(field_scores), 1)
    total = max(0.001, min(0.999, total))

    # Build feedback
    good = [f for f, s in field_scores.items() if s >= 0.8]
    partial = [f for f, s in field_scores.items() if 0.3 <= s < 0.8]
    bad = [f for f, s in field_scores.items() if s < 0.3]

    feedback_parts = []
    if good:
        feedback_parts.append(f"Correct: {', '.join(good)}")
    if partial:
        feedback_parts.append(f"Partially correct: {', '.join(partial)}")
    if bad:
        feedback_parts.append(f"Incorrect/missing: {', '.join(bad)}")

    feedback = " | ".join(feedback_parts) + f" | Score: {total:.2f}"
    return total, feedback


class InvoiceEnvironment:
    """
    InvoiceAI India — RL Environment for training AI agents
    to extract structured data from Indian GST invoices.
    """

    def __init__(self):
        self.state: Optional[InvoiceState] = None
        self.current_invoice: Optional[Dict[str, Any]] = None
        self.best_score: float = 0.0

    def reset(self, task_id: str = "easy") -> InvoiceObservation:
        """Start a new episode for a given task."""
        invoices = TASK_REGISTRY.get(task_id, TASK_REGISTRY["easy"])
        self.current_invoice = random.choice(invoices)

        self.state = InvoiceState(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            task_id=task_id,
            max_steps=5,
            current_score=0.0,
            attempts=0,
        )
        self.best_score = 0.0

        return InvoiceObservation(
            invoice_text=self.current_invoice["text"],
            task_id=task_id,
            task_description=self.current_invoice["task_description"],
            fields_to_extract=self.current_invoice["fields_to_extract"],
            feedback="New invoice loaded. Extract the required fields.",
            score=0.0,
            done=False,
        )

    def step(self, action: InvoiceAction) -> dict:
        """
        Agent submits an extraction attempt.
        Returns dict with observation, reward, done, info.
        """
        if self.state is None or self.current_invoice is None:
            return {
                "observation": InvoiceObservation(
                    feedback="Error: call reset() first.",
                    done=True,
                ).model_dump(),
                "reward": 0.0,
                "done": True,
            }

        self.state.step_count += 1
        self.state.attempts += 1

        # Grade the extraction
        score, feedback = grade_extraction(
            action,
            self.current_invoice["ground_truth"],
            self.current_invoice["fields_to_extract"],
        )

        # Reward = improvement over best previous score
        improvement = max(0.0, score - self.best_score)
        reward = improvement  # reward for getting better
        if score >= 0.95:
            reward += 0.5  # bonus for near-perfect extraction

        self.best_score = max(self.best_score, score)
        self.state.current_score = self.best_score

        # Check if episode is done
        done = (
            score >= 0.95  # near-perfect extraction
            or self.state.step_count >= self.state.max_steps  # max steps reached
        )

        obs = InvoiceObservation(
            invoice_text=self.current_invoice["text"],
            task_id=self.state.task_id,
            task_description=self.current_invoice["task_description"],
            fields_to_extract=self.current_invoice["fields_to_extract"],
            feedback=feedback,
            score=self.best_score,
            done=done,
        )

        return {
            "observation": obs.model_dump(),
            "reward": round(reward, 4),
            "done": done,
        }

    def get_state(self) -> dict:
        """Return current episode state."""
        if self.state is None:
            return InvoiceState().model_dump()
        return self.state.model_dump()
