#!/usr/bin/env python3
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
required = [
    "rail_core.py",
    "claim_pack.py",
    "test_rail_core.py",
    "index.html",
    "app.js",
    "style.css",
    "README.md",
    "sample_scenario.json",
    "sample_claim_pack.json",
    "sample_claim_pack.md",
]
missing = [p for p in required if not (BASE / p).exists()]
if missing:
    raise SystemExit(f"missing files: {missing}")
pack = json.loads((BASE / "sample_claim_pack.json").read_text(encoding="utf-8"))
assert pack["assessment"]["estimated_reimbursement_eur"] == 30.0
assert pack["assessment"]["reimbursement_rate"] == 0.25
assert "no es asesoría legal" in pack["assessment"]["disclaimer"]
runtime_text = "\n".join(
    (BASE / name).read_text(encoding="utf-8") for name in ["index.html", "style.css"]
)
for pattern in [
    r'<script[^>]+src=["\']https?://',
    r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']https?://',
    r'<img[^>]+src=["\']https?://',
    r'@import\s+url\(["\']?https?://',
    r'url\(["\']https?://',
]:
    if re.search(pattern, runtime_text, flags=re.I):
        raise SystemExit(f"remote runtime resource detected: {pattern}")
assert "Sin registro" in (BASE / "index.html").read_text(encoding="utf-8")
print(
    f"OK rail compensation pack files={len(required)} "
    f"estimated={pack['assessment']['estimated_reimbursement_eur']:.2f}"
)
