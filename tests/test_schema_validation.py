import json
import math
import pathlib
import copy
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
FIXTURE = ROOT / "tests" / "fixtures" / "agent_case_v1_1_minimal.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_registry():
    registry = Registry()
    for path in SCHEMAS.glob("*.json"):
        schema = load_json(path)
        resource = Resource.from_contents(schema)
        registry = registry.with_resource(schema["$id"], resource)
    return registry


def expected_case_status(module_statuses):
    values = list(module_statuses.values())
    if any(value == "failed" for value in values):
        return "failed"
    if values and all(value == "not_started" for value in values):
        return "created"
    if values and all(value == "completed" for value in values):
        return "completed"
    return "processing"


def expected_risk_level(loss):
    if loss < 5:
        return "low"
    if loss < 15:
        return "medium"
    if loss < 25:
        return "high"
    return "critical"


class SchemaValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = {path.name: load_json(path) for path in SCHEMAS.glob("*.json")}
        cls.registry = build_registry()
        cls.instance = load_json(FIXTURE)

    def test_all_schema_documents_are_valid_draft_2020_12(self):
        for name, schema in self.schemas.items():
            with self.subTest(schema=name):
                Draft202012Validator.check_schema(schema)

    def test_minimal_complete_case_matches_root_schema(self):
        validator = Draft202012Validator(
            self.schemas["agent_schema.json"],
            registry=self.registry,
            format_checker=FormatChecker(),
        )
        errors = sorted(validator.iter_errors(self.instance), key=lambda error: list(error.path))
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def test_all_top_level_tax_case_ids_match(self):
        expected = self.instance["tax_case"]["tax_case_id"]
        for key, value in self.instance.items():
            if isinstance(value, dict) and "tax_case_id" in value:
                with self.subTest(module=key):
                    self.assertEqual(expected, value["tax_case_id"])
        for event in self.instance["risk_events"]["risk_events"]:
            self.assertEqual(expected, event["tax_case_id"])

    def test_case_status_is_derived_from_module_statuses(self):
        tax_case = self.instance["tax_case"]
        self.assertEqual(expected_case_status(tax_case["module_statuses"]), tax_case["case_status"])

    def test_risk_scores_and_case_health_score_are_deterministic(self):
        scored_events = []
        for event in self.instance["risk_events"]["risk_events"]:
            scores = event["severity_scores"]
            weighted = (
                scores["tax_consequence_severity"] * 0.25
                + scores["tax_amount_impact"] * 0.20
                + scores["obligation_violation_severity"] * 0.30
                + scores["duration_severity"] * 0.15
                + scores["impact_scope"] * 0.10
            )
            self.assertAlmostEqual(weighted, event["weighted_severity"])
            self.assertAlmostEqual(weighted * 10, event["health_score_loss"])
            self.assertEqual(expected_risk_level(event["health_score_loss"]), event["risk_level"])
            if not event["suppressed_for_scoring"]:
                scored_events.append(event)

        total_loss = sum(event["health_score_loss"] for event in scored_events)
        score = math.floor(max(0, 100 - total_loss))
        result = self.instance["tax_health_score"]
        self.assertAlmostEqual(total_loss, result["total_health_score_loss"])
        self.assertEqual(score, result["tax_health_score"])

    def test_evidence_coverage_is_deterministic(self):
        result = self.instance["evidence_coverage"]
        raw_loss = 0
        for detail in result["evidence_loss_details"]:
            expected_loss = detail["configured_loss"] * detail["state_factor"]
            self.assertAlmostEqual(expected_loss, detail["actual_evidence_coverage_loss"])
            raw_loss += expected_loss
        total_loss = min(100, raw_loss)
        score = math.floor(max(0, 100 - total_loss))
        self.assertAlmostEqual(total_loss, result["total_evidence_coverage_loss"])
        self.assertEqual(score, result["evidence_coverage"])

    def test_next_actions_only_reference_formal_risk_events(self):
        risk_ids = {event["risk_event_id"] for event in self.instance["risk_events"]["risk_events"]}
        for action in self.instance["next_actions"]["next_actions"]:
            self.assertIn(action["related_risk_event_id"], risk_ids)

    def test_non_contract_source_cannot_have_contract_role(self):
        instance = copy.deepcopy(self.instance["tax_case"])
        instance["source_files"][0]["source_file_type"] = "invoice"
        validator = Draft202012Validator(
            self.schemas["tax_case_schema.json"],
            registry=self.registry,
            format_checker=FormatChecker(),
        )
        self.assertTrue(list(validator.iter_errors(instance)))

    def test_actual_event_cannot_use_legacy_status_field(self):
        instance = copy.deepcopy(self.instance["actual_facts"])
        instance["actual_payments"].append(
            {
                "actual_payment_id": "PAYMENT_001",
                "payment_date": "2026-08-20",
                "amount": 1000,
                "currency": "CNY",
                "status": "confirmed_done",
                "sources": [{"source_file_id": "FILE_PAYMENT_001"}],
            }
        )
        validator = Draft202012Validator(
            self.schemas["actual_facts_schema.json"],
            registry=self.registry,
            format_checker=FormatChecker(),
        )
        self.assertTrue(list(validator.iter_errors(instance)))

    def test_provided_evidence_requires_a_source_file(self):
        instance = {
            "tax_case_id": "CASE_001",
            "evidence_requirement_instances": [
                {
                    "evidence_requirement_instance_id": "EVIDENCE_INSTANCE_001",
                    "evidence_requirement_id": "payment_evidence",
                    "target_object_id": "PAYMENT_TERM_001",
                    "trigger_source_ids": ["PAYMENT_TERM_001"],
                    "period_start": None,
                    "period_end": None,
                    "check_due_date": "2026-08-20",
                }
            ],
            "evidence_states": [
                {
                    "evidence_state_id": "EVIDENCE_STATE_001",
                    "evidence_requirement_instance_id": "EVIDENCE_INSTANCE_001",
                    "state": "provided",
                    "related_actual_fact_ids": [],
                    "supporting_source_file_ids": [],
                }
            ],
        }
        validator = Draft202012Validator(
            self.schemas["evidence_schema.json"],
            registry=self.registry,
            format_checker=FormatChecker(),
        )
        self.assertTrue(list(validator.iter_errors(instance)))

    def test_unknown_judgement_atom_must_have_null_value(self):
        atom_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$ref": "https://tax-agent.local/schemas/common_defs_schema.json#/$defs/judgement_atom",
        }
        validator = Draft202012Validator(atom_schema, registry=self.registry)
        invalid_atom = {
            "status": "unknown",
            "value": True,
            "legal_basis_ids": [],
            "fact_basis_ids": [],
        }
        self.assertTrue(list(validator.iter_errors(invalid_atom)))


if __name__ == "__main__":
    unittest.main()
