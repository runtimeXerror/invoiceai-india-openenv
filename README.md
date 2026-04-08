---
title: InvoiceAI India - GST Invoice Extraction Environment
emoji: 🧾
colorFrom: yellow
colorTo: green
sdk: docker
app_port: 7860
tags:
  - openenv
pinned: false
---

# 🧾 InvoiceAI India — GST Invoice Data Extraction Environment

**An OpenEnv RL environment for training AI agents to extract structured data from Indian GST invoices.**

> India-first, GST-focused, real-world invoice extraction — the kind of task every accounting team, CA firm, and small business deals with daily.

---

## Why This Environment?

Manual invoice data entry costs accounting teams **40–70% of their billable hours** while introducing 1–3% error rates. India's GST regime (GSTIN, HSN codes, CGST/SGST/IGST splits, Place of Supply rules) adds complexity that generic global tools handle poorly.

This environment trains AI agents to:
- Parse unstructured invoice text into structured fields
- Handle Indian-specific formats (GSTIN validation, HSN codes, dual GST)
- Deal with messy, real-world formatting (abbreviations, inconsistent layouts, discounts)

---

## Environment Overview

### Action Space (`InvoiceAction`)

The agent submits extracted fields as a structured JSON:

| Field | Type | Description |
|-------|------|-------------|
| `vendor_name` | `str` | Business name on the invoice |
| `invoice_number` | `str` | Unique invoice identifier |
| `invoice_date` | `str` | Date in DD/MM/YYYY format |
| `gstin` | `str` | 15-character GST Identification Number |
| `total_amount` | `float` | Final grand total |
| `subtotal` | `float` | Amount before tax |
| `cgst` | `float` | Central GST amount |
| `sgst` | `float` | State GST amount |
| `igst` | `float` | Integrated GST amount |
| `line_items` | `list` | Array of `{description, hsn, qty, rate, amount}` |
| `currency` | `str` | Currency code (INR, USD, etc.) |
| `place_of_supply` | `str` | State name |
| `buyer_name` | `str` | Buyer/customer name |
| `buyer_gstin` | `str` | Buyer's GSTIN |

### Observation Space (`InvoiceObservation`)

| Field | Type | Description |
|-------|------|-------------|
| `invoice_text` | `str` | Raw invoice text to parse |
| `task_id` | `str` | `easy` / `medium` / `hard` |
| `task_description` | `str` | What the agent needs to do |
| `fields_to_extract` | `list[str]` | Which fields are expected |
| `feedback` | `str` | Grader feedback from last attempt |
| `score` | `float` | Current best score (0.0–1.0) |
| `done` | `bool` | Whether episode is complete |

---

## Tasks (Easy → Medium → Hard)

### Task 1: Easy — Basic Field Extraction
- **Objective:** Extract 5 core fields from a clean, well-formatted invoice
- **Fields:** vendor_name, invoice_number, invoice_date, gstin, total_amount
- **Expected Score Range:** 0.7–1.0
- **Challenge:** Minimal — standard formatting, clear labels

### Task 2: Medium — Full Invoice Parsing
- **Objective:** Extract 13 fields including line items and tax breakdown
- **Fields:** All basic fields + subtotal, CGST, SGST, buyer details, place of supply, line items with HSN codes
- **Expected Score Range:** 0.4–0.8
- **Challenge:** Multiple line items, tax calculation verification, buyer/seller distinction

### Task 3: Hard — Messy Real-World Invoice
- **Objective:** Extract all fields from an inconsistently formatted invoice
- **Fields:** Same as medium, but with IGST instead of CGST/SGST
- **Expected Score Range:** 0.2–0.6
- **Challenge:** Abbreviated dates (5-Jan-2026), discount percentages, IGST vs CGST/SGST logic, rounding adjustments, mixed units, informal layout

---

## Reward Function

The reward function provides **dense, partial-credit signals** — not sparse binary rewards:

- **String fields** (vendor_name, buyer_name): Fuzzy string similarity (0.0–1.0)
- **Numeric fields** (amounts): Tolerance-based scoring (exact=1.0, within 10%=0.5, within 25%=0.2)
- **Line items**: Per-item matching with field-level scoring (description, HSN, qty, amount)
- **Improvement reward**: Agent gets rewarded for improving over its previous best score
- **Perfect bonus**: +0.5 bonus for achieving ≥95% accuracy
- **Null handling**: Correctly identifying that CGST/SGST should be null for IGST invoices scores positively

---

## Setup & Usage

### 1. Run Locally

```bash
# Clone the repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/invoice-env
cd invoice-env

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn server.app:app --host 0.0.0.0 --port 7860

# Test health
curl http://localhost:7860/health
```

### 2. Docker

```bash
docker build -t invoice-env .
docker run -p 7860:7860 invoice-env
```

### 3. API Usage

```python
import requests

# Reset with a task
resp = requests.post("http://localhost:7860/reset", json={"task_id": "easy"})
obs = resp.json()["observation"]

# Submit extraction
action = {
    "vendor_name": "Sharma Electronics Pvt. Ltd.",
    "invoice_number": "SE/2025-26/0847",
    "invoice_date": "15/03/2026",
    "gstin": "09AABCS1429B1ZX",
    "total_amount": 37760.00
}
result = requests.post("http://localhost:7860/step", json=action)
print(result.json())
```

### 4. Run Baseline Inference

```bash
export HF_TOKEN="your-token"
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export INVOICE_ENV_URL="https://YOUR-SPACE.hf.space"

python inference.py
```

---

## Baseline Scores

| Task | Difficulty | Expected Score (Qwen2.5-72B) |
|------|-----------|------------------------------|
| Easy | ⭐ | 0.85–1.00 |
| Medium | ⭐⭐ | 0.50–0.75 |
| Hard | ⭐⭐⭐ | 0.30–0.55 |

---

## Grading Criteria

The grader is **100% deterministic** — no LLM-based judging:

1. Each field is compared against ground truth
2. String fields use `SequenceMatcher` for fuzzy matching
3. Numeric fields use percentage tolerance (2% for exact, 10% for partial)
4. Line items are matched using best-fit algorithm across all predicted items
5. Final score = average of all field scores (0.0–1.0)

---

## Project Structure

```
invoice_env/
├── README.md                    # This file
├── Dockerfile                   # HF Spaces deployment
├── openenv.yaml                 # OpenEnv manifest
├── pyproject.toml               # Package config
├── requirements.txt             # Dependencies
├── __init__.py                  # Module exports
├── models.py                    # Action, Observation, State (Pydantic)
├── client.py                    # HTTP client
├── inference.py                 # Baseline inference script
├── server/
│   ├── __init__.py
│   ├── invoice_environment.py   # Core env logic + graders
│   └── app.py                   # FastAPI application
└── data/
    ├── __init__.py
    └── invoices.py              # Sample GST invoices (3 levels)
```

---

## Tech Stack

- **Python 3.11** + **FastAPI** + **Pydantic v2**
- **OpenEnv** spec compliant (step/reset/state)
- **Docker** containerized
- **HuggingFace Spaces** deployment

---

## Author

Built by **Vishal** | [LaunchifyX](https://launchifyx.com) | OpenEnv Hackathon 2026

---

## License

BSD-3-Clause
