"""Deterministic Tax Health Score and Risk Level calculations."""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from math import floor
from typing import Any


WEIGHTS = {
    "tax_consequence_severity": Decimal("0.25"),
    "tax_amount_impact": Decimal("0.20"),
    "obligation_violation_severity": Decimal("0.30"),
    "duration_severity": Decimal("0.15"),
    "impact_scope": Decimal("0.10"),
}


def weighted_severity(scores: dict[str, int]) -> float:
    _validate_scores(scores)
    result = sum(Decimal(scores[name]) * weight for name, weight in WEIGHTS.items())
    return float(result)


def health_score_loss(scores: dict[str, int]) -> float:
    return float(Decimal(str(weighted_severity(scores))) * Decimal("10"))


def risk_level(loss: float) -> str:
    if loss < 0:
        raise ValueError("health_score_loss cannot be negative")
    if loss < 5:
        return "low"
    if loss < 15:
        return "medium"
    if loss < 25:
        return "high"
    return "critical"


def tax_amount_impact(amount_difference: float | None, transaction_amount: float | None) -> int:
    """Map deterministic absolute/relative tax difference to the higher score."""

    if amount_difference is None:
        return 0
    amount = abs(amount_difference)
    absolute = _bucket(amount, (0, 10_000, 50_000, 200_000))
    relative = 0
    if transaction_amount not in (None, 0):
        ratio = amount / abs(transaction_amount)
        relative = _bucket(ratio, (0, 0.01, 0.03, 0.10))
    return max(absolute, relative)


def duration_severity(days: int | None = None, periods: int | None = None) -> int:
    day_score = 0 if days is None else _bucket(max(days, 0), (0, 30, 90, 365))
    if periods is None or periods <= 0:
        period_score = 0
    elif periods == 1:
        period_score = 1
    elif periods <= 3:
        period_score = 2
    elif periods <= 12:
        period_score = 3
    else:
        period_score = 4
    return max(day_score, period_score)


def impact_scope(transaction_count: int | None, *, systemic: bool = False) -> int:
    if systemic:
        return 4
    if transaction_count is None or transaction_count <= 0:
        return 0
    if transaction_count == 1:
        return 1
    if transaction_count <= 3:
        return 2
    if transaction_count <= 10:
        return 3
    return 4


def score_risk_event(event: dict[str, Any]) -> dict[str, Any]:
    """Return a copy with derived severity, loss and Risk Level refreshed."""

    scored = deepcopy(event)
    loss = health_score_loss(scored["severity_scores"])
    scored["weighted_severity"] = weighted_severity(scored["severity_scores"])
    scored["health_score_loss"] = loss
    scored["risk_level"] = risk_level(loss)
    return scored


def calculate_tax_health_score(
    tax_case_id: str, risk_events: list[dict[str, Any]]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Score a Case with suppression and impact-group monetary de-duplication."""

    scored_events = [score_risk_event(event) for event in risk_events]
    amount_owner = _choose_amount_owner(scored_events)
    total_loss = Decimal("0")
    final_ids: list[str] = []

    for event in scored_events:
        if event.get("suppressed_for_scoring", False):
            continue
        final_ids.append(event["risk_event_id"])
        scores = dict(event["severity_scores"])
        group_id = event.get("impact_group_id")
        if group_id and amount_owner.get(group_id) != event["risk_event_id"]:
            scores["tax_amount_impact"] = 0
        total_loss += Decimal(str(health_score_loss(scores)))

    total_value = float(total_loss)
    output = {
        "tax_case_id": tax_case_id,
        "tax_health_score": floor(max(0, 100 - total_value)),
        "total_health_score_loss": total_value,
        "final_risk_event_ids": final_ids,
    }
    return output, scored_events


def collect_risk_codes(risk_events: list[dict[str, Any]]) -> list[str]:
    """Return unique confirmed formal risk codes in display order."""

    rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    active = [item for item in risk_events if not item.get("suppressed_for_scoring", False)]
    active.sort(key=lambda item: (rank[item["risk_level"]], -item["health_score_loss"]))
    return list(dict.fromkeys(item["risk_event_type"] for item in active))


def _validate_scores(scores: dict[str, int]) -> None:
    missing = set(WEIGHTS) - set(scores)
    if missing:
        raise ValueError(f"Missing scoring dimensions: {sorted(missing)}")
    for name in WEIGHTS:
        value = scores[name]
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 4:
            raise ValueError(f"{name} must be an integer from 0 to 4")


def _bucket(value: float, boundaries: tuple[float, float, float, float]) -> int:
    if value <= boundaries[0]:
        return 0
    if value <= boundaries[1]:
        return 1
    if value <= boundaries[2]:
        return 2
    if value <= boundaries[3]:
        return 3
    return 4


def _choose_amount_owner(events: list[dict[str, Any]]) -> dict[str, str]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        group_id = event.get("impact_group_id")
        if group_id and not event.get("suppressed_for_scoring", False):
            grouped.setdefault(group_id, []).append(event)

    owners: dict[str, str] = {}
    for group_id, members in grouped.items():
        members.sort(key=_monetary_priority)
        owners[group_id] = members[0]["risk_event_id"]
    return owners


def _monetary_priority(event: dict[str, Any]) -> tuple[int, int, str]:
    risk_type = event["risk_event_type"]
    if "underpayment" in risk_type or "underwithheld" in risk_type:
        priority = 0
    elif "overpayment" in risk_type:
        priority = 1
    else:
        priority = 2
    return (priority, -event["severity_scores"]["tax_amount_impact"], event["risk_event_id"])
