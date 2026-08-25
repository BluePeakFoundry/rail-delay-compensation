#!/usr/bin/env python3
"""Generate a local, editable EU rail delay compensation claim pack."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rail_core import assess, scenario_from_dict, to_dict

SOURCES = [
    "https://europa.eu/youreurope/citizens/travel/passenger-rights/rail/index_en.htm",
    "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32021R0782",
    "https://transport.ec.europa.eu/transport-themes/passenger-rights/rail-passenger-rights_en",
]


def claim_letter(s, a):
    return f"""Asunto: Reclamación informativa por retraso/cancelación del {s.train_number}

A la atención de {s.operator}:

Soy {s.passenger_description}. En relación con el {s.train_number} del {s.travel_date}, solicito revisar los derechos aplicables por {s.disruption_type} conforme a la normativa pública de derechos de pasajeros ferroviarios.

Datos orientativos:
- Precio del billete: {s.ticket_price_eur:.2f} €
- Retraso de llegada: {s.arrival_delay_minutes} minutos
- Estimación orientativa generada por la herramienta: {a.estimated_reimbursement_eur:.2f} € si la reclamación resulta aplicable y aceptada.

Adjuntaría, en una reclamación real, copia de billete/reserva, justificante de pago, hora prevista/real de llegada y comunicaciones del operador. Esta carta es un borrador editable y debe verificarse antes de enviarse.

Atentamente,
[Nombre del pasajero]
"""


def build_pack(scenario_path: Path):
    scenario_data = json.loads(scenario_path.read_text(encoding="utf-8"))
    scenario = scenario_from_dict(scenario_data)
    assessment = assess(scenario)
    return {
        "scenario": to_dict(scenario),
        "assessment": to_dict(assessment),
        "official_sources": SOURCES,
        "claim_letter_draft": claim_letter(scenario, assessment),
    }


def to_markdown(pack):
    a = pack["assessment"]
    s = pack["scenario"]
    reasons = "\n".join(f"- {r}" for r in a["reasons"])
    checks = "\n".join(f"- {c}" for c in a["required_user_checks"])
    sources = "\n".join(f"- {u}" for u in pack["official_sources"])
    return f"""# EU Rail Delay Compensation Pack

## Resultado orientativo

- Tren: {s['train_number']}
- Operador: {s['operator']}
- Elegible orientativo: {a['eligible']}
- Estimación orientativa: {a['estimated_reimbursement_eur']:.2f} €
- Tasa orientativa: {a['reimbursement_rate'] * 100:.0f}%
- Estado: {a['status']}

## Razones

{reasons}

## Comprobaciones de usuario necesarias

{checks}

## Fuentes oficiales

{sources}

## Borrador de carta editable

```text
{pack['claim_letter_draft']}
```

## Aviso

{a['disclaimer']}
"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", required=True)
    p.add_argument("--json", required=True)
    p.add_argument("--markdown", required=True)
    args = p.parse_args()
    pack = build_pack(Path(args.scenario))
    Path(args.json).write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(args.markdown).write_text(to_markdown(pack), encoding="utf-8")
    print(f"OK rail claim pack estimated={pack['assessment']['estimated_reimbursement_eur']:.2f}")


if __name__ == "__main__":
    main()
