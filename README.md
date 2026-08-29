# EU Rail Delay Compensation Calculator

Static, privacy-preserving calculator for preparing an educational estimate of minimum EU rail delay reimbursement rates and an editable draft message.

## What it does

- Estimates 25% of the ticket price for arrival delays from 60 to 119 minutes.
- Estimates 50% for arrival delays of 120 minutes or more.
- Generates local JSON, Markdown and browser draft text for review.
- Runs as a static page with no registration, no storage, no cookies, and privacy-friendly aggregate analytics for visits and events.

## What it does not do

- It is not legal advice.
- It does not submit claims, contact operators, collect personal data or guarantee payment.
- Users must verify the applicable operator procedure, conditions, exemptions, documentation and deadlines.

## Public sources to verify before real use

- Your Europe rail passenger rights.
- Regulation (EU) 2021/782.
- European Commission rail passenger rights.

## Local checks

```bash
python3 -m unittest -q
python3 claim_pack.py --scenario sample_scenario.json --json sample_claim_pack.json --markdown sample_claim_pack.md
python3 validate_pack.py
python3 validate_public_site.py
node --check app.js
```
