"""Judgement Resolution for Atomic Rule outputs."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Any


def resolve_judgements(executions: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate executions by target while respecting confirmation priority."""

    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for result in executions:
        grouped[result["target_judgement_item"]].append(result)

    resolutions = []
    for target in sorted(grouped):
        items = grouped[target]
        confirmed = [item for item in items if item["status"].startswith("confirmed_")]
        provisional = [item for item in items if item["status"].startswith("provisional_")]

        if confirmed:
            values = {item["value"] for item in confirmed}
            if len(values) == 1:
                resolution_status = "resolved"
                value = next(iter(values))
                conflicting_ids: list[str] = []
            else:
                resolution_status = "conflict"
                value = None
                conflicting_ids = [item["rule_execution_id"] for item in confirmed]
        elif provisional:
            values = {item["value"] for item in provisional}
            resolution_status = "conflict" if len(values) > 1 else "insufficient"
            value = None
            conflicting_ids = (
                [item["rule_execution_id"] for item in provisional]
                if resolution_status == "conflict"
                else []
            )
        else:
            resolution_status = "insufficient"
            value = None
            conflicting_ids = []

        resolutions.append(
            {
                "judgement_resolution_id": f"RESOLUTION_{_safe_id(target)}",
                "target_judgement_item": target,
                "resolution_status": resolution_status,
                "value": value,
                "legal_basis_ids": _union_ids(items, "legal_basis_ids"),
                "fact_basis_ids": _union_ids(items, "fact_basis_ids"),
                "supporting_rule_execution_ids": [
                    item["rule_execution_id"] for item in items
                ],
                "conflicting_rule_execution_ids": conflicting_ids,
            }
        )
    return resolutions


def _union_ids(items: Iterable[Mapping[str, Any]], field: str) -> list[str]:
    return sorted({identifier for item in items for identifier in item.get(field, [])})


def _safe_id(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._:-" else "_" for char in value)
