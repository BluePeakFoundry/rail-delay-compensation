"""Orientative EU rail passenger delay compensation calculations.

Conservative informational module. It does not send claims, store passenger data,
or contact rail operators. Users must verify eligibility with official sources.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List

SUPPORTED_DISRUPTIONS = {"delay", "cancellation"}


@dataclass(frozen=True)
class RailScenario:
    disruption_type: str
    ticket_price_eur: float
    arrival_delay_minutes: int
    journey_within_eu_or_operator_eu: bool
    informed_before_purchase: bool
    delay_due_to_passenger: bool
    exceptional_circumstances: bool
    accepted_refund_or_reroute: bool
    passenger_description: str = "pasajero/a"
    operator: str = "el operador ferroviario"
    train_number: str = "tren"
    travel_date: str = "fecha del viaje"


@dataclass(frozen=True)
class Assessment:
    eligible: bool
    estimated_reimbursement_eur: float
    reimbursement_rate: float
    status: str
    reasons: List[str]
    required_user_checks: List[str]
    disclaimer: str = "Estimación informativa basada en reglas públicas; no es asesoría legal y no garantiza compensación."


def reimbursement_rate_for_delay(delay_minutes: int) -> float:
    if delay_minutes < 0:
        raise ValueError("arrival_delay_minutes must be >= 0")
    if delay_minutes >= 120:
        return 0.50
    if delay_minutes >= 60:
        return 0.25
    return 0.0


def assess(s: RailScenario) -> Assessment:
    if s.disruption_type not in SUPPORTED_DISRUPTIONS:
        raise ValueError(f"unsupported disruption_type: {s.disruption_type}")
    if s.ticket_price_eur <= 0:
        raise ValueError("ticket_price_eur must be positive")

    checks = [
        "Verificar que el trayecto/operador cae bajo normas UE y si aplica alguna exención nacional o de servicio.",
        "Conservar billete, reserva, justificante de precio, hora prevista/real y comunicaciones del operador.",
        "Comprobar el procedimiento y plazo de reclamación del operador/autoridad nacional competente.",
        "Confirmar si hubo circunstancias excepcionales, información previa o culpa del pasajero que excluyan compensación.",
    ]

    if not s.journey_within_eu_or_operator_eu:
        return Assessment(False, 0.0, 0.0, "fuera_de_alcance", ["El trayecto indicado no parece cubierto por derechos ferroviarios UE en esta herramienta."], checks)
    if s.informed_before_purchase:
        return Assessment(False, 0.0, 0.0, "informado_antes_de_comprar", ["Si el pasajero fue informado del retraso antes de comprar el billete, la compensación puede no aplicar."], checks)
    if s.delay_due_to_passenger:
        return Assessment(False, 0.0, 0.0, "culpa_pasajero", ["El retraso indicado se atribuye al pasajero; no se estima compensación."], checks)
    if s.exceptional_circumstances:
        return Assessment(False, 0.0, 0.0, "posible_exclusion", ["Se indican circunstancias excepcionales; podrían excluir compensación económica aunque existan otros derechos."], checks)

    rate = reimbursement_rate_for_delay(s.arrival_delay_minutes)
    if rate == 0.0:
        return Assessment(False, 0.0, 0.0, "retraso_insuficiente", ["Retraso de llegada inferior a 60 minutos; no se estima compensación mínima por retraso."], checks)

    reasons: List[str] = []
    estimated = round(s.ticket_price_eur * rate, 2)
    reasons.append(f"Retraso de llegada {s.arrival_delay_minutes} min -> reembolso orientativo mínimo del {int(rate * 100)}% del billete.")
    reasons.append(f"Precio del billete {s.ticket_price_eur:.2f} € -> estimación orientativa {estimated:.2f} €.")
    if s.disruption_type == "cancellation":
        reasons.append("Cancelación: además de compensación por retraso en llegada, revisar derechos a reembolso/reruta y asistencia.")
    if s.accepted_refund_or_reroute:
        reasons.append("El pasajero indica que aceptó reembolso/reruta; verificar si eso modifica la compensación aplicable.")
    return Assessment(True, estimated, rate, "posible_reclamacion", reasons, checks)


def scenario_from_dict(d: Dict) -> RailScenario:
    return RailScenario(
        disruption_type=str(d["disruption_type"]),
        ticket_price_eur=float(d["ticket_price_eur"]),
        arrival_delay_minutes=int(d["arrival_delay_minutes"]),
        journey_within_eu_or_operator_eu=bool(d["journey_within_eu_or_operator_eu"]),
        informed_before_purchase=bool(d.get("informed_before_purchase", False)),
        delay_due_to_passenger=bool(d.get("delay_due_to_passenger", False)),
        exceptional_circumstances=bool(d.get("exceptional_circumstances", False)),
        accepted_refund_or_reroute=bool(d.get("accepted_refund_or_reroute", False)),
        passenger_description=str(d.get("passenger_description", "pasajero/a")),
        operator=str(d.get("operator", "el operador ferroviario")),
        train_number=str(d.get("train_number", "tren")),
        travel_date=str(d.get("travel_date", "fecha del viaje")),
    )


def to_dict(obj):
    return asdict(obj)
