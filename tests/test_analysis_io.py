from MEA.common.analysis_io import read_diagnostic_rows, write_diagnostic_rows


def test_nested_diagnostics_round_trip_through_flat_csv(tmp_path):
    path = tmp_path / "diagnostics.csv"
    rows = [
        {
            "block": "pressure",
            "identity": "pressure-1",
            "observed": 10.0,
            "predicted": 9.0,
            "status": "evaluated",
        },
        {
            "block": "speciation",
            "identity": "state-1",
            "status": "evaluated",
            "target_count": 2,
            "targets": [
                {
                    "identity": "state-1::MEACOO-",
                    "observed": 0.1,
                    "predicted": 0.09,
                },
                {
                    "identity": "state-1::MEA",
                    "observed": 0.2,
                    "predicted": 0.21,
                },
            ],
        },
    ]

    write_diagnostic_rows(path, rows)

    flat = read_diagnostic_rows(path)
    assert len(flat) == 3
    assert flat[1]["state_identity"] == "state-1"
    assert flat[1]["target_identity"] == "state-1::MEACOO-"
    nested = read_diagnostic_rows(path, nested=True)
    assert [row["identity"] for row in nested] == ["pressure-1", "state-1"]
    assert [row["identity"] for row in nested[1]["targets"]] == [
        "state-1::MEACOO-",
        "state-1::MEA",
    ]
    assert nested[1]["target_count"] == "2"


def test_empty_diagnostics_keep_a_readable_csv(tmp_path):
    path = tmp_path / "diagnostics.csv"
    write_diagnostic_rows(path, [])
    assert read_diagnostic_rows(path, nested=True) == []
