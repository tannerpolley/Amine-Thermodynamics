from MEA.common.film_chemistry_inputs import validate_film_chemistry_inputs


def test_work_package_a_inputs_fail_closed_and_conserve_balances() -> None:
    report = validate_film_chemistry_inputs()
    assert report["status"] == "pass"
    assert report["net_carbamate_balance"] == {
        "C": 0,
        "H": 0,
        "N": 0,
        "O": 0,
        "charge": 0,
    }
    assert report["admitted_fast_equilibrium_reactions"] == []
    assert report["admitted_numeric_transport_inputs"] == []
    assert report["provider_activity_correction_ran"] is False
