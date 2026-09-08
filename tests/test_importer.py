from app.importer import parse_cr, parse_meta, parse_speeds, parse_xp, text_from_html


def test_parses_fractional_challenge_rating_and_xp():
    assert parse_cr("1/4 (50 XP)") == 0.25
    assert parse_xp("10 (5,900 XP)") == 5900


def test_parses_meta_and_movement():
    assert parse_meta("Large aberration, lawful evil") == ("Large", "aberration", "lawful evil")
    assert parse_speeds("40 ft., burrow 30 ft., fly 80 ft.") == {
        "walk": 40, "fly": 80, "swim": None, "climb": None, "burrow": 30,
    }


def test_converts_html_features_to_searchable_text():
    assert text_from_html("<p><strong>Flyby.</strong> The owl doesn't provoke.</p>") == "Flyby. The owl doesn't provoke."
