from app.query import parse_rules


def test_rules_parser_builds_expected_filters():
    plan = parse_rules("medium undead CR 5 or lower immune to poison")
    assert {(item.field, item.operator, item.value) for item in plan.filters} == {
        ("size", "eq", "Medium"),
        ("creature_type", "eq", "undead"),
        ("challenge_rating", "lte", 5.0),
        ("damage_immunity", "contains", "poison"),
    }


def test_rules_parser_supports_stat_comparisons():
    plan = parse_rules("dragons with strength 20 or higher")
    assert any(item.field == "creature_type" and item.value == "dragon" for item in plan.filters)
    assert any(item.field == "strength" and item.operator == "gte" and item.value == 20 for item in plan.filters)
