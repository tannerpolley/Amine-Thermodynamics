from analyses.amines import displays


def test_typed_number_exception_belongs_to_one_context(tmp_path, monkeypatch):
    path = tmp_path / "experiment.tex"
    record = "From 20 states, the retained count was 20."
    path.write_text(record)
    # The synthetic manuscript is outside the repo. Point the checked display source
    # into the fixture too, so file identities use the same repository-relative form.
    renderer = tmp_path / "displays.py"
    renderer.write_text("")
    monkeypatch.setattr(displays, "__file__", str(renderer))
    monkeypatch.setattr(displays, "ROOT", tmp_path)
    monkeypatch.setattr(displays, "manuscript_sources", lambda: [path])
    values = {"reported-count": {"value": "20"}}
    reviewed = [{"file": "experiment.tex", "context": "From 20 states", "token": "20", "reason": "condition"}]
    assert list(displays.typed_numbers(values, reviewed)) == ["Typed result candidate: experiment.tex:1: 20"]
    path.write_text(r"From 20 states, the retained count was \res{reported-count}.")
    assert not list(displays.typed_numbers(values, reviewed))

    path.write_text("\n\n" + r"From 20 states, the retained count was \res{reported-count}.")
    assert not list(displays.typed_numbers(values, reviewed))

    path.write_text("From 20 states\nFrom 20 states")
    assert list(displays.typed_numbers(values, reviewed)) == [
        "Stale or ambiguous number collision: experiment.tex: From 20 states"
    ]

    path.write_text(r"From 21 states, the retained count was \res{reported-count}.")
    assert list(displays.typed_numbers(values, reviewed)) == [
        "Stale or ambiguous number collision: experiment.tex: From 20 states"
    ]

    path.write_text(r"From 20 states, the retained count was \res{reported-count}.")
    assert list(displays.typed_numbers({"reported-count": {"value": "21"}}, reviewed)) == [
        "Stale or ambiguous number collision: experiment.tex: From 20 states"
    ]


def test_typed_range_upper_limit_is_unsigned():
    text = r"Prescribed 10--20 wt\%; the residual is -20\%."
    assert [(match[0], value) for match, value in displays.numeric_occurrences(text, text)] == [
        ("10", 10), ("20", 20), ("-20", -20)
    ]
