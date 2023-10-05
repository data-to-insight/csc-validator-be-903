from lac_validator.rule_engine import RuleDefinition


def test_ruledefinition():
    rule = RuleDefinition(
        code="203",
        message="Test error",
        affected_fields=["SOME_FIELD"],
        func=lambda x: x == 1,
    )

    assert rule.code == "203"
    assert rule.message == "Test error"
    assert rule.affected_fields == ["SOME_FIELD"]
