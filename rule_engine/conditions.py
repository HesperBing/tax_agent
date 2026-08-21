"""Tri-state evaluation for deterministic Atomic Rule conditions.

The evaluator deliberately distinguishes:

* a missing path;
* the business value ``unknown``;
* the business value ``pending``; and
* an ordinary true/false comparison.

Neither ``unknown`` nor ``pending`` is silently converted into a confirmed
violation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


TRUE = "true"
FALSE = "false"
UNKNOWN = "unknown"
PENDING = "pending"


class ConditionEvaluationError(ValueError):
    """Raised when a condition configuration is invalid."""


_MISSING = object()


def resolve_json_pointer(document: Any, pointer: str) -> Any:
    """Resolve a JSON Pointer and return a private sentinel when absent."""

    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ConditionEvaluationError(f"Invalid JSON Pointer: {pointer!r}")

    current = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            if token not in current:
                return _MISSING
            current = current[token]
        elif isinstance(current, Sequence) and not isinstance(current, (str, bytes)):
            try:
                index = int(token)
                current = current[index]
            except (ValueError, IndexError):
                return _MISSING
        else:
            return _MISSING
    return current


def evaluate_condition(condition: Mapping[str, Any], context: Any) -> str:
    """Evaluate one condition and return true/false/unknown/pending."""

    condition_type = condition.get("condition_type")
    if condition_type == "semantic_condition":
        # Semantic conditions require a controlled external evaluator.  The
        # deterministic v0.1 engine never guesses their result.
        return UNKNOWN
    if condition_type != "deterministic_condition":
        raise ConditionEvaluationError(f"Unsupported condition type: {condition_type!r}")

    operator = condition.get("operator")
    actual = resolve_json_pointer(context, condition.get("fact_path", ""))
    expected = condition.get("expected_value")

    if operator == "exists":
        return TRUE if actual is not _MISSING else FALSE
    if operator == "not_exists":
        return TRUE if actual is _MISSING else FALSE
    if actual is _MISSING:
        return UNKNOWN

    # An explicit rule is allowed to inspect the literal status.  Otherwise
    # unknown/pending must propagate instead of becoming an ordinary value.
    if actual == "unknown" and expected != "unknown":
        return UNKNOWN
    if actual == "pending" and expected != "pending":
        return PENDING

    try:
        matched = _compare(actual, operator, expected)
    except (TypeError, ValueError) as exc:
        raise ConditionEvaluationError(
            f"Cannot evaluate {operator!r} for actual={actual!r}, expected={expected!r}"
        ) from exc
    return TRUE if matched else FALSE


def evaluate_conditions(conditions: Sequence[Mapping[str, Any]], context: Any) -> str:
    """Combine an AND list of conditions without erasing uncertainty."""

    if not conditions:
        raise ConditionEvaluationError("An Atomic Rule must contain at least one condition")

    outcomes = [evaluate_condition(condition, context) for condition in conditions]
    if FALSE in outcomes:
        return FALSE
    if PENDING in outcomes:
        return PENDING
    if UNKNOWN in outcomes:
        return UNKNOWN
    return TRUE


def _compare(actual: Any, operator: str, expected: Any) -> bool:
    if operator == "eq":
        return actual == expected
    if operator == "ne":
        return actual != expected
    if operator == "gt":
        return actual > expected
    if operator == "gte":
        return actual >= expected
    if operator == "lt":
        return actual < expected
    if operator == "lte":
        return actual <= expected
    if operator == "in":
        return actual in expected
    if operator == "not_in":
        return actual not in expected
    if operator == "contains":
        return expected in actual
    raise ConditionEvaluationError(f"Unsupported operator: {operator!r}")
