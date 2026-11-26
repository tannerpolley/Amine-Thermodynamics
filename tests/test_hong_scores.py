from analyses.amines.mea import hong_scores


def test_models_are_scored_on_the_same_rows():
    rows = [
        dict(block="wagner", three_model_eligible=True, record_id=k, observed=10.0,
             predicted=p, adopted=a, polley_hedengren_2026=11.0, adopted_role="not fitted")
        for k, p, a in (("r1", 11.0, 12.0), ("r2", 15.0, None))
    ]
    (score,) = [s for s in hong_scores(rows) if s["subset"] == "all"]
    assert score["n"] == 1 and score["unavailable"] == ["r2"]
    # Hong is scored on r1 only, as the adopted model is: |11 - 10| / 10 = 10 %.
    assert abs(score["hong"] - 10.0) < 1e-12
