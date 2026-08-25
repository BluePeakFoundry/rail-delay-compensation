# EU Rail Delay Compensation Pack

Activo local de coste cero para generar una estimación educativa de compensación/reembolso por retraso ferroviario bajo derechos de pasajeros UE.

## Qué hace

- Calcula 25% del precio del billete para retrasos de llegada de 60 a 119 minutos.
- Calcula 50% para retrasos de 120 minutos o más.
- Genera JSON, Markdown y una carta editable.

## Qué no hace

- No es asesoría legal.
- No publica, cobra, contacta operadores ni envía reclamaciones.
- No recopila datos reales ni usa recursos remotos.
- No garantiza que una reclamación sea aceptada.

## Fuentes públicas a verificar antes de uso real

- Your Europe Rail passenger rights
- Regulation (EU) 2021/782
- European Commission rail passenger rights

## Pruebas

```bash
python3 -m unittest -v
python3 claim_pack.py --scenario sample_scenario.json --json sample_claim_pack.json --markdown sample_claim_pack.md
python3 validate_pack.py
```
