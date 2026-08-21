"""Rule Engine façade used by tests and the future Dify tool endpoint."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .atomic import execute_atomic_rule
from .resolution import resolve_judgements


class UnknownRuleIdError(KeyError):
    """Raised when a caller asks for a Rule ID that is not registered."""


class RuleEngine:
    def __init__(self, rule_config: Mapping[str, Any]):
        if rule_config.get("version") != "v1.1":
            raise ValueError("Rule configuration must target Schema v1.1")
        rules = rule_config.get("atomic_rules", [])
        self._rules: dict[str, Mapping[str, Any]] = {}
        for rule in rules:
            rule_id = rule["rule_id"]
            if rule_id in self._rules:
                raise ValueError(f"Duplicate Rule ID: {rule_id}")
            self._rules[rule_id] = rule

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._rules))

    def match_rule(self, rule_id: str) -> Mapping[str, Any]:
        try:
            return self._rules[rule_id]
        except KeyError as exc:
            raise UnknownRuleIdError(rule_id) from exc

    def run(
        self,
        rule_engine_input: Mapping[str, Any],
        context: Mapping[str, Any],
        *,
        rule_ids: Iterable[str] | None = None,
        legal_basis_by_target: Mapping[str, list[str]] | None = None,
        fact_basis_by_rule: Mapping[str, list[str]] | None = None,
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Execute selected Rules and return Schema output plus diagnostics."""

        if rule_engine_input["tax_case_id"] != context["tax_case_id"]:
            raise ValueError("Rule Engine Input and context tax_case_id must match")

        selected_ids = list(rule_ids) if rule_ids is not None else list(self.rule_ids)
        legal_basis_by_target = legal_basis_by_target or {}
        fact_basis_by_rule = fact_basis_by_rule or {}
        executions: list[dict[str, Any]] = []
        diagnostics: list[dict[str, Any]] = []

        for rule_id in selected_ids:
            rule = self.match_rule(rule_id)
            result, trace = execute_atomic_rule(
                rule,
                context,
                legal_basis_ids=legal_basis_by_target.get(rule["target_judgement_item"], []),
                fact_basis_ids=fact_basis_by_rule.get(rule_id, []),
            )
            executions.append(result)
            diagnostics.append(trace)

        output = {
            "tax_case_id": rule_engine_input["tax_case_id"],
            "rule_execution_results": executions,
            "judgement_resolution_results": resolve_judgements(executions),
        }
        return output, diagnostics
