#!/usr/bin/env python3
import json
import re
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(__file__).resolve().parent
PUBLIC_URL = "https://bluepeakfoundry.github.io/rail-delay-compensation/"
FORBIDDEN_INTERNAL = [
    "sergi", "rex-money", "autonomous agent", "ciclo", "money verified",
    "dinero verificado", "monetization_matrix", "approval gate", "workspace",
]
REMOTE_RUNTIME_PATTERNS = [
    r'<script[^>]+src=["\']https?://',
    r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']https?://',
    r'<img[^>]+src=["\']https?://',
    r'@import\s+url\(["\']?https?://',
    r'url\(["\']https?://',
]
REQUIRED = [
    "index.html", "app.js", "style.css", "README.md", "robots.txt", "sitemap.xml",
    "rail_core.py", "claim_pack.py", "test_rail_core.py", "validate_pack.py",
]

class LDParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_ld = False
        self.blocks = []
        self._buf = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_ld = True
            self._buf = []

    def handle_data(self, data):
        if self.in_ld:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.in_ld:
            self.blocks.append("".join(self._buf))
            self.in_ld = False

missing = [name for name in REQUIRED if not (BASE / name).exists()]
if missing:
    raise SystemExit(f"missing required files: {missing}")
html = (BASE / "index.html").read_text(encoding="utf-8")
css = (BASE / "style.css").read_text(encoding="utf-8")
js = (BASE / "app.js").read_text(encoding="utf-8")
readme = (BASE / "README.md").read_text(encoding="utf-8")
robots = (BASE / "robots.txt").read_text(encoding="utf-8")
sitemap = (BASE / "sitemap.xml").read_text(encoding="utf-8")
all_public_text = "\n".join([html, css, js, readme, robots, sitemap]).lower()
for term in FORBIDDEN_INTERNAL:
    if term in all_public_text:
        raise SystemExit(f"forbidden internal term in public files: {term}")
for pattern in REMOTE_RUNTIME_PATTERNS:
    if re.search(pattern, html + "\n" + css, flags=re.I):
        raise SystemExit(f"remote runtime resource detected: {pattern}")
checks = {
    "canonical": f'<link rel="canonical" href="{PUBLIC_URL}">' in html,
    "description": '<meta name="description"' in html,
    "robots_meta": '<meta name="robots" content="index,follow">' in html,
    "og": 'property="og:title"' in html and 'property="og:url"' in html,
    "skip_link": 'class="skip-link"' in html and 'href="#calculator"' in html,
    "labels": '<label for="ticket"' in html and '<label for="delay"' in html,
    "help_text": 'aria-describedby="ticket-help"' in html and 'aria-describedby="delay-help"' in html,
    "live_region": 'aria-live="polite"' in html and 'aria-atomic="true"' in html,
    "faq_visible": '<section class="card faq"' in html and '<details' in html,
    "privacy": "Sin registro" in html and "Sin almacenamiento" in html and "analytics" in readme.lower(),
    "draft": 'id="draft"' in html and 'draftText' in js,
    "robots": "User-agent: *" in robots and PUBLIC_URL + "sitemap.xml" in robots,
    "sitemap": PUBLIC_URL in sitemap,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit(f"public site checks failed: {failed}")
parser = LDParser()
parser.feed(html)
if len(parser.blocks) != 1:
    raise SystemExit(f"expected 1 JSON-LD block, found {len(parser.blocks)}")
ld = json.loads(parser.blocks[0])
ld_text = json.dumps(ld)
if "SoftwareApplication" not in ld_text or "FAQPage" not in ld_text:
    raise SystemExit("missing SoftwareApplication/FAQPage JSON-LD")
pack = json.loads((BASE / "sample_claim_pack.json").read_text(encoding="utf-8"))
if pack.get("money_verified_eur", 0) != 0:
    raise SystemExit("money safeguard failed")
if pack.get("external_actions_performed", []) != []:
    raise SystemExit("external action safeguard failed")
print("OK public rail site files=10 no_remote_runtime_resources privacy_safeguards_present seo_accessibility_present")
