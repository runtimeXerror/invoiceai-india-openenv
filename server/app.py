"""
InvoiceAI India — FastAPI Server
Exposes OpenEnv-compatible endpoints: /reset, /step, /state, /health
Plus a web interface at /web for interactive testing.
"""

import sys
import os

# Ensure parent dir is on path so models + data can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

from models import InvoiceAction
from server.invoice_environment import InvoiceEnvironment

app = FastAPI(
    title="InvoiceAI India — GST Invoice Extraction Environment",
    description="An OpenEnv RL environment for training AI agents to extract structured data from Indian GST invoices.",
    version="1.0.0",
)

# Global environment instance (per-worker; for hackathon single-user is fine)
env = InvoiceEnvironment()


class ResetRequest(BaseModel):
    task_id: Optional[str] = "easy"


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    obs = env.reset(task_id=req.task_id or "easy")
    return {"observation": obs.model_dump()}


@app.post("/step")
def step(action: InvoiceAction):
    result = env.step(action)
    return result


@app.get("/state")
def state():
    return env.get_state()


@app.get("/", response_class=HTMLResponse)
@app.get("/web", response_class=HTMLResponse)
def web_interface():
    return WEB_HTML


WEB_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>InvoiceAI India — GST Invoice Extraction</title>
<style>
  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #242836;
    --border: #2e3345;
    --accent: #f97316;
    --accent2: #22c55e;
    --text: #e2e8f0;
    --text2: #94a3b8;
    --red: #ef4444;
    --blue: #3b82f6;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }
  /* Header */
  .header {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-bottom: 1px solid var(--border);
    padding: 20px 32px;
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .header .logo { font-size: 36px; }
  .header h1 { font-size: 22px; font-weight: 700; }
  .header h1 span { color: var(--accent); }
  .header .badge {
    background: var(--accent);
    color: #000;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .header .subtitle { color: var(--text2); font-size: 13px; margin-top: 2px; }

  /* Layout */
  .container { display: grid; grid-template-columns: 1fr 1fr; gap: 0; min-height: calc(100vh - 80px); }
  @media (max-width: 900px) { .container { grid-template-columns: 1fr; } }

  /* Panels */
  .panel { padding: 24px; overflow-y: auto; }
  .panel-left { border-right: 1px solid var(--border); }

  .panel-title {
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text2);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .panel-title .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent2);
    display: inline-block;
  }

  /* Task selector */
  .task-selector { display: flex; gap: 8px; margin-bottom: 20px; }
  .task-btn {
    flex: 1;
    padding: 10px 16px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--surface);
    color: var(--text2);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
  }
  .task-btn:hover { border-color: var(--accent); color: var(--text); }
  .task-btn.active {
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
  }
  .task-btn .diff { font-size: 11px; display: block; margin-top: 2px; opacity: 0.8; }

  /* Invoice display */
  .invoice-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    font-family: 'Courier New', monospace;
    font-size: 12.5px;
    line-height: 1.6;
    white-space: pre-wrap;
    max-height: 55vh;
    overflow-y: auto;
    color: #c8d6e5;
  }

  .fields-needed {
    margin-top: 16px;
    padding: 12px 16px;
    background: rgba(249,115,22,0.08);
    border: 1px solid rgba(249,115,22,0.2);
    border-radius: 8px;
    font-size: 13px;
  }
  .fields-needed strong { color: var(--accent); }

  /* Form */
  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .form-group { display: flex; flex-direction: column; }
  .form-group.full { grid-column: 1 / -1; }
  .form-group label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text2);
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .form-group input, .form-group textarea {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 12px;
    color: var(--text);
    font-size: 13px;
    font-family: inherit;
    outline: none;
    transition: border 0.2s;
  }
  .form-group input:focus, .form-group textarea:focus {
    border-color: var(--accent);
  }
  .form-group textarea { min-height: 80px; resize: vertical; }

  /* Submit button */
  .submit-btn {
    width: 100%;
    margin-top: 16px;
    padding: 12px;
    background: linear-gradient(135deg, var(--accent), #ea580c);
    color: #fff;
    font-size: 14px;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: opacity 0.2s;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .submit-btn:hover { opacity: 0.9; }
  .submit-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  /* Results */
  .result-card {
    margin-top: 20px;
    padding: 16px;
    border-radius: 10px;
    border: 1px solid var(--border);
    display: none;
  }
  .result-card.show { display: block; }
  .result-card.success { border-color: var(--accent2); background: rgba(34,197,94,0.06); }
  .result-card.partial { border-color: var(--accent); background: rgba(249,115,22,0.06); }
  .result-card.fail { border-color: var(--red); background: rgba(239,68,68,0.06); }

  .score-display {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    margin: 8px 0;
  }
  .score-label { text-align: center; font-size: 13px; color: var(--text2); }
  .feedback-text { margin-top: 12px; font-size: 13px; line-height: 1.6; color: var(--text2); }
  .reward-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 8px;
  }

  /* Status bar */
  .status-bar {
    display: flex;
    justify-content: space-between;
    padding: 8px 32px;
    background: var(--surface);
    border-top: 1px solid var(--border);
    font-size: 12px;
    color: var(--text2);
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
  }
  .status-bar .green { color: var(--accent2); }
</style>
</head>
<body>

<div class="header">
  <div class="logo">🧾</div>
  <div>
    <h1>Invoice<span>AI</span> India</h1>
    <div class="subtitle">India-first GST Invoice Data Extraction — OpenEnv RL Environment</div>
  </div>
  <div class="badge">OpenEnv Hackathon 2026</div>
</div>

<div class="container">
  <!-- LEFT PANEL: Invoice Display -->
  <div class="panel panel-left">
    <div class="panel-title"><span class="dot"></span> Invoice Preview</div>

    <div class="task-selector">
      <button class="task-btn active" onclick="loadTask('easy')" id="btn-easy">
        Easy <span class="diff">⭐ 5 fields</span>
      </button>
      <button class="task-btn" onclick="loadTask('medium')" id="btn-medium">
        Medium <span class="diff">⭐⭐ 13 fields</span>
      </button>
      <button class="task-btn" onclick="loadTask('hard')" id="btn-hard">
        Hard <span class="diff">⭐⭐⭐ Messy</span>
      </button>
    </div>

    <div class="invoice-box" id="invoice-text">Click a task above to load an invoice...</div>

    <div class="fields-needed" id="fields-info" style="display:none;">
      <strong>Fields to extract:</strong> <span id="fields-list"></span>
    </div>
  </div>

  <!-- RIGHT PANEL: Extraction Form -->
  <div class="panel">
    <div class="panel-title"><span class="dot" style="background:var(--blue)"></span> Your Extraction</div>

    <div class="form-grid">
      <div class="form-group"><label>Vendor Name</label><input id="f-vendor_name" placeholder="e.g. Sharma Electronics Pvt. Ltd."></div>
      <div class="form-group"><label>Invoice Number</label><input id="f-invoice_number" placeholder="e.g. SE/2025-26/0847"></div>
      <div class="form-group"><label>Invoice Date</label><input id="f-invoice_date" placeholder="DD/MM/YYYY"></div>
      <div class="form-group"><label>GSTIN</label><input id="f-gstin" placeholder="15-char GSTIN"></div>
      <div class="form-group"><label>Total Amount</label><input id="f-total_amount" type="number" step="0.01" placeholder="0.00"></div>
      <div class="form-group"><label>Subtotal</label><input id="f-subtotal" type="number" step="0.01" placeholder="0.00"></div>
      <div class="form-group"><label>CGST</label><input id="f-cgst" type="number" step="0.01" placeholder="0.00"></div>
      <div class="form-group"><label>SGST</label><input id="f-sgst" type="number" step="0.01" placeholder="0.00"></div>
      <div class="form-group"><label>IGST</label><input id="f-igst" type="number" step="0.01" placeholder="0.00"></div>
      <div class="form-group"><label>Currency</label><input id="f-currency" placeholder="INR"></div>
      <div class="form-group"><label>Place of Supply</label><input id="f-place_of_supply" placeholder="e.g. Delhi"></div>
      <div class="form-group"><label>Buyer Name</label><input id="f-buyer_name" placeholder="Buyer company name"></div>
      <div class="form-group"><label>Buyer GSTIN</label><input id="f-buyer_gstin" placeholder="Buyer's 15-char GSTIN"></div>
      <div class="form-group full">
        <label>Line Items (JSON array)</label>
        <textarea id="f-line_items" placeholder='[{"description":"Item","hsn":"8471","qty":5,"rate":1000,"amount":5000}]'></textarea>
      </div>
    </div>

    <button class="submit-btn" id="submit-btn" onclick="submitExtraction()" disabled>
      🚀 Submit Extraction
    </button>

    <div class="result-card" id="result-card">
      <div class="score-label">EXTRACTION SCORE</div>
      <div class="score-display" id="score-display">0.00</div>
      <div style="text-align:center;">
        <span class="reward-badge" id="reward-badge">Reward: 0.00</span>
      </div>
      <div class="feedback-text" id="feedback-text"></div>
    </div>
  </div>
</div>

<div class="status-bar">
  <span>🧾 InvoiceAI India v1.0.0 | OpenEnv Hackathon 2026</span>
  <span>Status: <span class="green">● Connected</span></span>
  <span id="step-info">Steps: 0/5</span>
</div>

<script>
let currentTask = '';
let stepCount = 0;

async function loadTask(taskId) {
  document.querySelectorAll('.task-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-' + taskId).classList.add('active');
  currentTask = taskId;
  stepCount = 0;

  // Clear form
  document.querySelectorAll('.form-grid input, .form-grid textarea').forEach(el => el.value = '');
  document.getElementById('result-card').classList.remove('show','success','partial','fail');

  try {
    const resp = await fetch('/reset', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({task_id: taskId})
    });
    const data = await resp.json();
    const obs = data.observation;

    document.getElementById('invoice-text').textContent = obs.invoice_text;
    document.getElementById('fields-info').style.display = 'block';
    document.getElementById('fields-list').textContent = obs.fields_to_extract.join(', ');
    document.getElementById('submit-btn').disabled = false;
    document.getElementById('step-info').textContent = 'Steps: 0/5';
  } catch(e) {
    document.getElementById('invoice-text').textContent = 'Error loading invoice: ' + e.message;
  }
}

async function submitExtraction() {
  const action = {};
  const textFields = ['vendor_name','invoice_number','invoice_date','gstin','currency','place_of_supply','buyer_name','buyer_gstin'];
  const numFields = ['total_amount','subtotal','cgst','sgst','igst'];

  textFields.forEach(f => {
    const val = document.getElementById('f-' + f).value.trim();
    if (val) action[f] = val;
  });
  numFields.forEach(f => {
    const val = document.getElementById('f-' + f).value.trim();
    if (val) action[f] = parseFloat(val);
  });

  const liVal = document.getElementById('f-line_items').value.trim();
  if (liVal) {
    try { action.line_items = JSON.parse(liVal); } catch(e) { /* ignore parse errors */ }
  }

  try {
    const resp = await fetch('/step', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(action)
    });
    const data = await resp.json();
    const obs = data.observation;
    const reward = data.reward;
    const score = obs.score;

    stepCount++;
    document.getElementById('step-info').textContent = `Steps: ${stepCount}/5`;

    // Show result
    const card = document.getElementById('result-card');
    card.classList.add('show');
    card.classList.remove('success','partial','fail');
    if (score >= 0.8) card.classList.add('success');
    else if (score >= 0.4) card.classList.add('partial');
    else card.classList.add('fail');

    document.getElementById('score-display').textContent = score.toFixed(2);
    document.getElementById('score-display').style.color =
      score >= 0.8 ? 'var(--accent2)' : score >= 0.4 ? 'var(--accent)' : 'var(--red)';

    const rb = document.getElementById('reward-badge');
    rb.textContent = `Reward: +${reward.toFixed(2)}`;
    rb.style.background = reward > 0 ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)';
    rb.style.color = reward > 0 ? 'var(--accent2)' : 'var(--red)';

    document.getElementById('feedback-text').textContent = obs.feedback;

    if (obs.done) {
      document.getElementById('submit-btn').disabled = true;
      document.getElementById('submit-btn').textContent = score >= 0.95
        ? '✅ PERFECT EXTRACTION!'
        : '⏹ Episode Complete — Select New Task';
    }
  } catch(e) {
    alert('Error: ' + e.message);
  }
}

// Auto-load easy task on page load
window.onload = () => loadTask('easy');
</script>
</body>
</html>"""


def main():
    import uvicorn
    port = int(os.environ.get("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()