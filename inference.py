"""
InvoiceAI India — Baseline Inference Script
============================================
Uses OpenAI-compatible client to run an LLM agent against the
Invoice Data Extraction environment across all 3 tasks.

Required env vars:
    API_BASE_URL   LLM API endpoint
    MODEL_NAME     Model identifier
    HF_TOKEN       API key
"""

import json
import os
import sys
import textwrap
from typing import Any, Dict, List, Optional

import requests
from openai import OpenAI

# ── Configuration ─────────────────────────────────────────────────────────────
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or ""
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
ENV_URL = os.getenv("INVOICE_ENV_URL") or "https://YOUR-HF-SPACE.hf.space"

BENCHMARK = "invoice_extraction"
MAX_STEPS = 3
TEMPERATURE = 0.3
MAX_TOKENS = 2000

TASKS = ["easy", "medium", "hard"]

SYSTEM_PROMPT = textwrap.dedent("""
You are an expert AI agent that extracts structured data from Indian GST invoices.
You will be given the raw text of an invoice and a list of fields to extract.
You MUST respond with ONLY a valid JSON object containing the extracted fields.
Do NOT include any explanation, markdown, or text before or after the JSON.

Field guidelines:
- vendor_name: Company/business name that issued the invoice
- invoice_number: Unique invoice identifier
- invoice_date: In DD/MM/YYYY format
- gstin: 15-character GST Identification Number of the vendor
- total_amount: Final grand total amount as a number
- subtotal: Amount before tax as a number
- cgst: Central GST amount as a number (null if not applicable)
- sgst: State GST amount as a number (null if not applicable)
- igst: Integrated GST amount as a number (null if not applicable)
- buyer_name: Name of the buyer/customer
- buyer_gstin: GSTIN of the buyer
- place_of_supply: State name
- currency: Currency code (usually "INR")
- line_items: Array of objects with keys: description, hsn, qty, rate, amount

Respond ONLY with the JSON object.
""").strip()


# ── Logging helpers ───────────────────────────────────────────────────────────
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    error_val = error if error else "null"
    done_val = str(done).lower()
    action_clean = action.replace("\n", " ")[:200]
    print(f"[STEP] step={step} action={action_clean} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)


# ── LLM Call ──────────────────────────────────────────────────────────────────
def call_llm(client: OpenAI, invoice_text: str, fields: List[str], feedback: str = "") -> Dict[str, Any]:
    """Ask the LLM to extract fields from the invoice text."""
    user_msg = f"Invoice text:\n```\n{invoice_text}\n```\n\nFields to extract: {json.dumps(fields)}"
    if feedback:
        user_msg += f"\n\nPrevious attempt feedback: {feedback}\nPlease correct the errors."

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()

        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()
        if text.startswith("json"):
            text = text[4:].strip()

        return json.loads(text)
    except json.JSONDecodeError:
        print(f"[DEBUG] Failed to parse LLM JSON response", flush=True)
        return {}
    except Exception as exc:
        print(f"[DEBUG] LLM call failed: {exc}", flush=True)
        return {}


# ── Main ──────────────────────────────────────────────────────────────────────
def run_task(client: OpenAI, task_id: str):
    """Run one task episode."""
    log_start(task=f"invoice-{task_id}", env=BENCHMARK, model=MODEL_NAME)

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    try:
        # Reset environment
        reset_resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id}, timeout=30)
        reset_resp.raise_for_status()
        reset_data = reset_resp.json()

        obs = reset_data["observation"]
        invoice_text = obs["invoice_text"]
        fields = obs["fields_to_extract"]
        feedback = ""

        for step_num in range(1, MAX_STEPS + 1):
            # Get LLM extraction
            extracted = call_llm(client, invoice_text, fields, feedback)

            # Submit to environment
            step_resp = requests.post(f"{ENV_URL}/step", json=extracted, timeout=30)
            step_resp.raise_for_status()
            step_data = step_resp.json()

            obs = step_data["observation"]
            reward = step_data.get("reward", 0.0)
            done = step_data.get("done", False)

            rewards.append(reward)
            steps_taken = step_num
            feedback = obs.get("feedback", "")
            score = obs.get("score", 0.0)

            action_str = f"extract({task_id})"
            log_step(step=step_num, action=action_str, reward=reward, done=done, error=None)

            if done:
                break

        success = score >= 0.5
        score = min(max(score, 0.0), 1.0)

    except Exception as exc:
        print(f"[DEBUG] Task {task_id} error: {exc}", flush=True)
        score = 0.0

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    print("=" * 60)
    print("InvoiceAI India — Baseline Inference")
    print("=" * 60)

    total_score = 0.0
    for task_id in TASKS:
        print(f"\n{'─' * 40}")
        print(f"Running task: {task_id}")
        print(f"{'─' * 40}")
        task_score = run_task(client, task_id)
        total_score += task_score
        print(f"Task {task_id} score: {task_score:.2f}")

    avg_score = total_score / len(TASKS)
    print(f"\n{'=' * 60}")
    print(f"Average score across all tasks: {avg_score:.2f}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
