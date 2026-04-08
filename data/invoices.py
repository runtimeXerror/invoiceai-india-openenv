"""
InvoiceAI India — Sample Indian GST invoices for all 3 tasks.
Each invoice has raw text + ground truth for deterministic grading.
"""

from typing import Any, Dict, List

# ═══════════════════════════════════════════════════════════════════════════════
# TASK 1 — EASY: Simple invoice, 4 basic fields
# ═══════════════════════════════════════════════════════════════════════════════

EASY_INVOICES: List[Dict[str, Any]] = [
    {
        "id": "easy_001",
        "text": """
TAX INVOICE
─────────────────────────────────
Sharma Electronics Pvt. Ltd.
GSTIN: 09AABCS1429B1ZX
Shop No. 42, Nehru Place, New Delhi - 110019

Invoice No: SE/2025-26/0847
Date: 15/03/2026

Bill To: Cash Customer

Sr.  Description          HSN      Qty   Rate      Amount
1    LED TV 43 inch       8528     1     32,000    32,000.00

                                    Subtotal:      32,000.00
                                    CGST @9%:       2,880.00
                                    SGST @9%:       2,880.00
                                    ─────────────────────────
                                    Total:         37,760.00

Payment: UPI
Thank you for shopping with us!
""",
        "ground_truth": {
            "vendor_name": "Sharma Electronics Pvt. Ltd.",
            "invoice_number": "SE/2025-26/0847",
            "invoice_date": "15/03/2026",
            "gstin": "09AABCS1429B1ZX",
            "total_amount": 37760.00,
        },
        "fields_to_extract": ["vendor_name", "invoice_number", "invoice_date", "gstin", "total_amount"],
        "task_description": "Extract basic fields from a simple Indian GST invoice: vendor name, invoice number, date, GSTIN, and total amount.",
    },
    {
        "id": "easy_002",
        "text": """
TAX INVOICE

Gupta Medical Store
GSTIN: 10AADCG5678H1Z5
Main Road, Patna, Bihar - 800001

Invoice No: GMS-9921
Date: 02/01/2026

Sold To: Walk-in Customer

Item                     HSN     Qty    Rate     Amount
Paracetamol 500mg        3004     2     25.00     50.00
Cough Syrup 100ml        3004     1    120.00    120.00

                                  Subtotal:       170.00
                                  CGST @6%:        10.20
                                  SGST @6%:        10.20
                                  ─────────────────────
                                  Grand Total:     190.40

Mode of Payment: Cash
""",
        "ground_truth": {
            "vendor_name": "Gupta Medical Store",
            "invoice_number": "GMS-9921",
            "invoice_date": "02/01/2026",
            "gstin": "10AADCG5678H1Z5",
            "total_amount": 190.40,
        },
        "fields_to_extract": ["vendor_name", "invoice_number", "invoice_date", "gstin", "total_amount"],
        "task_description": "Extract basic fields from a simple Indian GST invoice: vendor name, invoice number, date, GSTIN, and total amount.",
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 2 — MEDIUM: Multi-line-item invoice with tax breakdown
# ═══════════════════════════════════════════════════════════════════════════════

MEDIUM_INVOICES: List[Dict[str, Any]] = [
    {
        "id": "medium_001",
        "text": """
TAX INVOICE
═══════════════════════════════════════════════════════════
  Kumar IT Solutions LLP
  GSTIN: 07AABFK2345M1ZP
  B-12, Connaught Place, New Delhi - 110001
  Phone: +91-11-23456789  |  Email: billing@kumarit.in

  Invoice No: KIT/2025/INV-3042
  Date: 28/02/2026
  Due Date: 30/03/2026
  Place of Supply: Delhi (07)

  Bill To:
    Patel Enterprises
    GSTIN: 07AABCP9876N1Z3
    45 Rajouri Garden, New Delhi - 110027
═══════════════════════════════════════════════════════════

Sr  Description                  HSN/SAC   Qty   Rate        Amount
──  ───────────────────────────  ────────  ───   ─────────   ──────────
1   Laptop Dell Inspiron 15      8471.30    5    55,000.00   2,75,000.00
2   Wireless Mouse Logitech      8471.60   10       800.00       8,000.00
3   USB-C Hub 7-in-1             8473.30    5     1,200.00       6,000.00
4   Laptop Bag Premium           4202.12    5       950.00       4,750.00
5   Annual AMC Service           998314     5     3,500.00      17,500.00

                                              Subtotal:     3,11,250.00
                                              CGST @9%:       28,012.50
                                              SGST @9%:       28,012.50
                                              ──────────────────────────
                                              Grand Total:  3,67,275.00

  Amount in Words: Three Lakh Sixty Seven Thousand Two Hundred Seventy Five Rupees Only
  Payment Terms: Net 30 days
  Bank Details: HDFC Bank, A/C: 50100123456789, IFSC: HDFC0001234

  Authorized Signatory
  Kumar IT Solutions LLP
""",
        "ground_truth": {
            "vendor_name": "Kumar IT Solutions LLP",
            "invoice_number": "KIT/2025/INV-3042",
            "invoice_date": "28/02/2026",
            "gstin": "07AABFK2345M1ZP",
            "total_amount": 367275.00,
            "subtotal": 311250.00,
            "cgst": 28012.50,
            "sgst": 28012.50,
            "buyer_name": "Patel Enterprises",
            "buyer_gstin": "07AABCP9876N1Z3",
            "place_of_supply": "Delhi",
            "currency": "INR",
            "line_items": [
                {"description": "Laptop Dell Inspiron 15", "hsn": "8471.30", "qty": 5, "rate": 55000.00, "amount": 275000.00},
                {"description": "Wireless Mouse Logitech", "hsn": "8471.60", "qty": 10, "rate": 800.00, "amount": 8000.00},
                {"description": "USB-C Hub 7-in-1", "hsn": "8473.30", "qty": 5, "rate": 1200.00, "amount": 6000.00},
                {"description": "Laptop Bag Premium", "hsn": "4202.12", "qty": 5, "rate": 950.00, "amount": 4750.00},
                {"description": "Annual AMC Service", "hsn": "998314", "qty": 5, "rate": 3500.00, "amount": 17500.00},
            ],
        },
        "fields_to_extract": [
            "vendor_name", "invoice_number", "invoice_date", "gstin",
            "total_amount", "subtotal", "cgst", "sgst",
            "buyer_name", "buyer_gstin", "place_of_supply", "currency", "line_items",
        ],
        "task_description": (
            "Extract all fields from a multi-item Indian GST invoice including: "
            "vendor details, buyer details, all line items with HSN codes, "
            "tax breakdown (CGST/SGST), subtotal, total, and place of supply."
        ),
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 3 — HARD: Messy/inconsistent invoice with edge cases
# ═══════════════════════════════════════════════════════════════════════════════

HARD_INVOICES: List[Dict[str, Any]] = [
    {
        "id": "hard_001",
        "text": """
                        PROFORMA CUM TAX INVOICE
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Singh & Sons Trading Co
    (Regd. under GST)  GSTN: 06AALFS3344K1Z8
    Opp. Old Bus Stand , JIND  Haryana 126102
    Mob- 94168-XXXXX
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Inv.  : SS/E-2026/00193             Dt.: 5-Jan-2026
    Reverse Charge: No
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    BILL TO :                       SHIP TO:
    Rajesh Agro Industries          Same as Billing
    GSTN 06BBBPR7722A1ZQ
    Village Uchana, Jind, HR

    Sl  Particulars          HSN     Qty  Unit  Rate     Disc%  Taxable Val
    --  --------------------  ------  ---  ----  -------  -----  -----------
    1   Submersible Pump 5HP  8413    2    Nos   18500    5%     35,150.00
    2   PVC Pipe 4" (100ft)   3917    3    Bndl   4200    -      12,600.00
    3   Elbow Joint 4"        3917    12   Pcs      85    10%       918.00
    4   Wire 2.5sqmm (Coil)  8544     2   Coil   3200    -       6,400.00
    5   Starter DOL 5HP       8536    2    Nos    2800    -       5,600.00
    6   Installation Chgs     995411  1    Job    4500    -       4,500.00
                                                        ─────────────────
                                              Total Taxable:    65,168.00

    IGST @18% (Inter-state supply):                             11,730.24

    Rounding Off:                                                    1.76
                                                        ─────────────────
    GRAND TOTAL:                        Rs.  76,900.00
    (Rupees Seventy Six Thousand Nine Hundred Only)

    Terms:
    1. Goods once sold will not be taken back
    2. Subject to Jind jurisdiction
    3. E&OE

    For Singh & Sons Trading Co
    (Authorised Signatory)
""",
        "ground_truth": {
            "vendor_name": "Singh & Sons Trading Co",
            "invoice_number": "SS/E-2026/00193",
            "invoice_date": "05/01/2026",
            "gstin": "06AALFS3344K1Z8",
            "total_amount": 76900.00,
            "subtotal": 65168.00,
            "igst": 11730.24,
            "cgst": None,
            "sgst": None,
            "buyer_name": "Rajesh Agro Industries",
            "buyer_gstin": "06BBBPR7722A1ZQ",
            "place_of_supply": "Haryana",
            "currency": "INR",
            "line_items": [
                {"description": "Submersible Pump 5HP", "hsn": "8413", "qty": 2, "rate": 18500.0, "amount": 35150.00},
                {"description": "PVC Pipe 4\" (100ft)", "hsn": "3917", "qty": 3, "rate": 4200.0, "amount": 12600.00},
                {"description": "Elbow Joint 4\"", "hsn": "3917", "qty": 12, "rate": 85.0, "amount": 918.00},
                {"description": "Wire 2.5sqmm (Coil)", "hsn": "8544", "qty": 2, "rate": 3200.0, "amount": 6400.00},
                {"description": "Starter DOL 5HP", "hsn": "8536", "qty": 2, "rate": 2800.0, "amount": 5600.00},
                {"description": "Installation Chgs", "hsn": "995411", "qty": 1, "rate": 4500.0, "amount": 4500.00},
            ],
        },
        "fields_to_extract": [
            "vendor_name", "invoice_number", "invoice_date", "gstin",
            "total_amount", "subtotal", "igst",
            "buyer_name", "buyer_gstin", "place_of_supply", "currency", "line_items",
        ],
        "task_description": (
            "Extract all fields from a messy, inconsistently formatted Indian GST invoice. "
            "Challenges: abbreviated date format, discount percentages applied to line items, "
            "IGST instead of CGST/SGST (inter-state supply), rounding adjustments, "
            "mixed units, and informal formatting. "
            "Handle missing/null fields correctly (e.g., CGST/SGST should be null for IGST invoices)."
        ),
    },
]


# ── Task registry ────────────────────────────────────────────────────────────
TASK_REGISTRY = {
    "easy": EASY_INVOICES,
    "medium": MEDIUM_INVOICES,
    "hard": HARD_INVOICES,
}
