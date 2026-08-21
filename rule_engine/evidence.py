"""Evidence Coverage, evidence gaps, unknown and pending helpers."""

from __future__ import annotations

from math import floor
from typing import Any


STATE_FACTORS = {"provided": 0, "unknown": 0.5, "missing": 1}
ALLOWED_CONFIGURED_LOSS = {6, 8, 10, 12}


def calculate_evidence_coverage(
    tax_case_id: str,
    requirement_instances: list[dict[str, Any]],
    evidence_states: list[dict[str, Any]],
    requirements: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Calculate coverage by active Requirement Instance, not by file count."""

    states_by_instance: dict[str, dict[str, Any]] = {}
    for state in evidence_states:
        instance_id = state["evidence_requirement_instance_id"]
        if instance_id in states_by_instance:
            raise ValueError(f"Duplicate Evidence State for {instance_id}")
        states_by_instance[instance_id] = state

    details: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    raw_loss = 0.0

    for instance in requirement_instances:
        instance_id = instance["evidence_requirement_instance_id"]
        state_record = states_by_instance.get(instance_id)
        # No State means a future/unreached check and therefore no score.
        if state_record is None or state_record["state"] == "not_applicable":
            continue

        requirement_id = instance["evidence_requirement_id"]
        if requirement_id not in requirements:
            raise KeyError(f"Unknown Evidence Requirement: {requirement_id}")
        configured_loss = requirements[requirement_id]["configured_loss"]
        if configured_loss not in ALLOWED_CONFIGURED_LOSS:
            raise ValueError(f"Invalid configured_loss for {requirement_id}")

        state = state_record["state"]
        factor = STATE_FACTORS[state]
        actual_loss = configured_loss * factor
        raw_loss += actual_loss
        details.append(
            {
                "evidence_requirement_instance_id": instance_id,
                "evidence_requirement_id": requirement_id,
                "evidence_state_id": state_record["evidence_state_id"],
                "state": state,
                "configured_loss": configured_loss,
                "state_factor": factor,
                "actual_evidence_coverage_loss": actual_loss,
            }
        )
        if state in {"missing", "unknown"}:
            gaps.append(
                {
                    "item_id": f"GAP_{instance_id}",
                    "text": f"{requirement_id} 的证据状态为 {state}",
                    "related_object_ids": [instance_id, state_record["evidence_state_id"]],
                }
            )

    total_loss = min(100, raw_loss)
    output = {
        "tax_case_id": tax_case_id,
        "evidence_coverage": floor(max(0, 100 - total_loss)),
        "total_evidence_coverage_loss": total_loss,
        "evidence_loss_details": details,
    }
    return output, gaps


def partition_business_statuses(
    records: list[dict[str, Any]], *, id_field: str = "item_id", status_field: str = "status"
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Create Final Report-style pending/unknown items without treating them as risks."""

    pending_items: list[dict[str, Any]] = []
    unknown_items: list[dict[str, Any]] = []
    for record in records:
        status = record.get(status_field)
        if status not in {"pending", "unknown"}:
            continue
        identifier = record[id_field]
        item = {
            "item_id": f"{status.upper()}_{identifier}",
            "text": record.get("text") or f"{identifier} 当前状态为 {status}",
            "related_object_ids": [identifier],
        }
        if status == "pending":
            pending_items.append(item)
        else:
            unknown_items.append(item)
    return pending_items, unknown_items
