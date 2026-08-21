"""Deterministic Rule Engine helpers for Tax Agent v0.1."""

from .engine import RuleEngine, UnknownRuleIdError
from .evidence import calculate_evidence_coverage, partition_business_statuses
from .resolution import resolve_judgements
from .scoring import (
    calculate_tax_health_score,
    collect_risk_codes,
    health_score_loss,
    risk_level,
    weighted_severity,
)

__all__ = [
    "RuleEngine",
    "UnknownRuleIdError",
    "calculate_evidence_coverage",
    "partition_business_statuses",
    "resolve_judgements",
    "calculate_tax_health_score",
    "collect_risk_codes",
    "health_score_loss",
    "risk_level",
    "weighted_severity",
]
