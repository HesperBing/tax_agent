import copy
import json
import pathlib
import sys
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT if (ROOT / "schemas").exists() else ROOT.parent / "tax_agent_schema_v1_1"
SCHEMAS = PROJECT_ROOT / "schemas"
sys.path.insert(0, str(ROOT))

from rule_engine.conditions import PENDING, UNKNOWN, evaluate_condition  # noqa: E402
from rule_engine.engine import RuleEngine, UnknownRuleIdError  # noqa: E402
from rule_engine.evidence import (  # noqa: E402
    calculate_evidence_coverage,
    partition_business_statuses,
)
from rule_engine.resolution import resolve_judgements  # noqa: E402
from rule_engine.scoring import (  # noqa: E402
    calculate_tax_health_score,
    collect_risk_codes,
    duration_severity,
    health_score_loss,
    impact_scope,
    risk_level,
    tax_amount_impact,
    weighted_severity,
)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_schema_registry():
    registry = Registry()
    for path in SCHEMAS.glob("*.json"):
        schema = load_json(path)
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


def assert_valid(test_case, instance, schema, registry):
    validator = Draft202012Validator(
        schema, registry=registry, format_checker=FormatChecker()
    )
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    test_case.assertEqual([], errors, "\n".join(error.message for error in errors))


class RuleEngineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_json(ROOT / "rules" / "tax" / "atomic_rules_v0_1.json")
        cls.rule_input = load_json(ROOT / "mocks" / "rule_engine_input_mock.json")
        cls.context = load_json(ROOT / "mocks" / "rule_engine_context_mock.json")
        cls.expected_output = load_json(ROOT / "mocks" / "rule_engine_output_mock.json")
        cls.engine = RuleEngine(cls.rules)

    def test_rule_id_matches_exact_registered_rule(self):
        rule = self.engine.match_rule("RULE_IIT_WITHHOLDING_APPLICABILITY_001")
        self.assertEqual("withholding_obligation_applicability", rule["target_judgement_item"])

    def test_unknown_rule_id_is_rejected(self):
        with self.assertRaises(UnknownRuleIdError):
            self.engine.match_rule("RULE_DOES_NOT_EXIST")

    def test_duplicate_rule_id_is_rejected(self):
        invalid = copy.deepcopy(self.rules)
        invalid["atomic_rules"].append(copy.deepcopy(invalid["atomic_rules"][0]))
        with self.assertRaises(ValueError):
            RuleEngine(invalid)

    def test_engine_output_matches_mock(self):
        output, diagnostics = self.engine.run(
            self.rule_input,
            self.context,
            legal_basis_by_target={
                "withholding_obligation_applicability": ["LAW_IIT_003"]
            },
            fact_basis_by_rule={
                "RULE_IIT_FILING_COMPLETION_001": ["FILING_STAGE_MOCK_001"],
                "RULE_IIT_WITHHOLDING_APPLICABILITY_001": [
                    "TRANSACTION_MOCK_001",
                    "REGULATION_MOCK_001",
                ],
                "RULE_IIT_WITHHOLDING_EVIDENCE_001": ["EVIDENCE_STATE_MOCK_001"],
            },
        )
        self.assertEqual(self.expected_output, output)
        self.assertTrue(any(item["contains_pending"] for item in diagnostics))
        self.assertTrue(any(item["contains_unknown"] for item in diagnostics))

    def test_pending_and_unknown_are_not_confirmed_violations(self):
        pending = {
            "condition_type": "deterministic_condition",
            "fact_path": "/status",
            "operator": "eq",
            "expected_value": "confirmed_done",
        }
        unknown = dict(pending)
        self.assertEqual(PENDING, evaluate_condition(pending, {"status": "pending"}))
        self.assertEqual(UNKNOWN, evaluate_condition(unknown, {"status": "unknown"}))

    def test_confirmed_conflict_is_not_silently_resolved(self):
        executions = [
            {
                "rule_execution_id": "EXEC_A",
                "target_judgement_item": "same_target",
                "status": "confirmed_triggered",
                "value": True,
                "legal_basis_ids": ["LAW_A"],
                "fact_basis_ids": ["FACT_A"],
            },
            {
                "rule_execution_id": "EXEC_B",
                "target_judgement_item": "same_target",
                "status": "confirmed_not_triggered",
                "value": False,
                "legal_basis_ids": ["LAW_B"],
                "fact_basis_ids": ["FACT_B"],
            },
        ]
        result = resolve_judgements(executions)[0]
        self.assertEqual("conflict", result["resolution_status"])
        self.assertIsNone(result["value"])


class ScoringTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.risk_module = load_json(ROOT / "mocks" / "risk_events_mock.json")
        cls.expected_score = load_json(ROOT / "mocks" / "tax_health_score_mock.json")

    def test_weighted_formula(self):
        scores = {
            "tax_consequence_severity": 3,
            "tax_amount_impact": 2,
            "obligation_violation_severity": 4,
            "duration_severity": 1,
            "impact_scope": 1,
        }
        self.assertEqual(2.6, weighted_severity(scores))
        self.assertEqual(26, health_score_loss(scores))

    def test_risk_level_boundaries(self):
        expected = [(0, "low"), (4.99, "low"), (5, "medium"), (15, "high"), (25, "critical")]
        for loss, level in expected:
            with self.subTest(loss=loss):
                self.assertEqual(level, risk_level(loss))

    def test_dynamic_scoring_mappings(self):
        self.assertEqual(4, tax_amount_impact(210_000, 10_000_000))
        self.assertEqual(3, tax_amount_impact(60_000, 1_000_000))
        self.assertEqual(3, duration_severity(days=120, periods=2))
        self.assertEqual(4, impact_scope(1, systemic=True))

    def test_case_score_and_risk_codes_match_mocks(self):
        score, scored_events = calculate_tax_health_score(
            self.risk_module["tax_case_id"], self.risk_module["risk_events"]
        )
        self.assertEqual(self.expected_score, score)
        self.assertEqual(
            ["withholding_obligation_not_performed", "invoice_incorrect_item"],
            collect_risk_codes(scored_events),
        )

    def test_suppressed_event_does_not_reduce_score(self):
        events = copy.deepcopy(self.risk_module["risk_events"])
        events[1]["suppressed_for_scoring"] = True
        score, _ = calculate_tax_health_score(self.risk_module["tax_case_id"], events)
        self.assertEqual(74, score["tax_health_score"])
        self.assertEqual(26, score["total_health_score_loss"])


class EvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = load_json(ROOT / "mocks" / "evidence_context_mock.json")
        cls.expected = load_json(ROOT / "mocks" / "evidence_coverage_mock.json")
        registry = load_json(
            ROOT / "registries" / "evidence_requirement_registry_v0_1.json"
        )
        cls.requirements = {
            item["evidence_requirement_id"]: item for item in registry["requirements"]
        }

    def test_evidence_coverage_and_gaps(self):
        output, gaps = calculate_evidence_coverage(
            self.context["tax_case_id"],
            self.context["evidence_requirement_instances"],
            self.context["evidence_states"],
            self.requirements,
        )
        self.assertEqual(self.expected, output)
        self.assertEqual(2, len(gaps))
        self.assertTrue(any("missing" in item["text"] for item in gaps))
        self.assertTrue(any("unknown" in item["text"] for item in gaps))

    def test_pending_and_unknown_go_to_separate_report_lists(self):
        records = load_json(ROOT / "mocks" / "business_status_mock.json")["items"]
        pending, unknown = partition_business_statuses(records)
        self.assertEqual(1, len(pending))
        self.assertEqual(1, len(unknown))
        self.assertIn("PENDING_", pending[0]["item_id"])
        self.assertIn("UNKNOWN_", unknown[0]["item_id"])


class MockSchemaValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCHEMAS.exists():
            raise RuntimeError(f"Schema directory not found: {SCHEMAS}")
        cls.schemas = {path.name: load_json(path) for path in SCHEMAS.glob("*.json")}
        cls.registry = build_schema_registry()

    def test_requested_module_mocks_match_schema_v1_1(self):
        cases = {
            "transaction_facts_mock.json": self.schemas["transaction_facts_schema.json"],
            "regulation_result_mock.json": self.schemas["regulation_result_schema.json"],
            "rule_engine_input_mock.json": self.schemas["rule_engine_input_schema.json"],
            "rule_engine_output_mock.json": self.schemas["rule_engine_output_schema.json"],
            "tax_judgement_mock.json": self.schemas["tax_judgement_schema.json"],
            "risk_events_mock.json": self.schemas["risk_event_schema.json"],
            "evidence_context_mock.json": self.schemas["evidence_schema.json"],
        }
        for filename, schema in cases.items():
            with self.subTest(mock=filename):
                assert_valid(
                    self, load_json(ROOT / "mocks" / filename), schema, self.registry
                )

    def test_score_mocks_match_schema_v1_1(self):
        cases = {
            "tax_health_score_mock.json": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$ref": "https://tax-agent.local/schemas/scoring_schema.json#/$defs/tax_health_score",
            },
            "evidence_coverage_mock.json": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$ref": "https://tax-agent.local/schemas/scoring_schema.json#/$defs/evidence_coverage",
            },
        }
        for filename, schema in cases.items():
            with self.subTest(mock=filename):
                assert_valid(
                    self, load_json(ROOT / "mocks" / filename), schema, self.registry
                )

    def test_rule_configuration_matches_schema_v1_1(self):
        assert_valid(
            self,
            load_json(ROOT / "rules" / "tax" / "atomic_rules_v0_1.json"),
            self.schemas["rule_schema.json"],
            self.registry,
        )

    def test_evidence_registry_entries_match_schema_v1_1(self):
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$ref": "https://tax-agent.local/schemas/evidence_schema.json#/$defs/evidence_requirement",
        }
        entries = load_json(
            ROOT / "registries" / "evidence_requirement_registry_v0_1.json"
        )["requirements"]
        for entry in entries:
            with self.subTest(requirement=entry["evidence_requirement_id"]):
                assert_valid(self, entry, schema, self.registry)


if __name__ == "__main__":
    unittest.main()
