"""Atomic Rule execution."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .conditions import FALSE, PENDING, TRUE, UNKNOWN, evaluate_conditions


_OPPOSITE_STATUS = {
    "confirmed_triggered": "confirmed_not_triggered",
    "confirmed_not_triggered": "confirmed_triggered",
    "provisional_triggered": "provisional_not_triggered",
    "provisional_not_triggered": "provisional_triggered",
    "unknown": "unknown",
}


def execute_atomic_rule(
    rule: Mapping[str, Any],
    context: Mapping[str, Any],
    *,
    legal_basis_ids: list[str] | None = None,
    fact_basis_ids: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Execute one Atomic Rule and return schema output plus diagnostics."""

    outcome = evaluate_conditions(rule["conditions"], context)
    configured_status = rule["rule_result_status"]

    if outcome == TRUE:
        status = configured_status
    elif outcome == FALSE:
        status = _OPPOSITE_STATUS[configured_status]
    else:
        # Business unknown and pending are both non-confirming Rule results.
        status = "unknown"

    if status.endswith("triggered") and not status.endswith("not_triggered"):
        value: bool | None = True
    elif status.endswith("not_triggered"):
        value = False
    else:
        value = None

    result = {
        "rule_execution_id": f"EXEC_{rule['rule_id']}",
        "rule_id": rule["rule_id"],
        "target_judgement_item": rule["target_judgement_item"],
        "status": status,
        "value": value,
        "legal_basis_ids": sorted(set(legal_basis_ids or [])),
        "fact_basis_ids": sorted(set(fact_basis_ids or [])),
        "evaluated_condition_ids": [item["condition_id"] for item in rule["conditions"]],
    }
    diagnostics = {
        "rule_id": rule["rule_id"],
        "condition_outcome": outcome,
        "contains_unknown": outcome == UNKNOWN,
        "contains_pending": outcome == PENDING,
    }
    return result, diagnostics
