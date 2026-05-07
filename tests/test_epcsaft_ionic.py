from __future__ import annotations

import unittest

import numpy as np

from MEA.epcsaft_ionic.model import DEFAULT_INITIAL_GUESS, load_speciation_targets, load_vle_targets, predict_co2_pressure_kPa


class IonicEPCSAFTWorkflowTests(unittest.TestCase):
    def test_ionic_targets_load_with_full_species_vectors(self) -> None:
        vle = load_vle_targets(2)
        speciation = load_speciation_targets(2)
        self.assertEqual(len(vle), 2)
        self.assertEqual(len(speciation), 2)
        self.assertEqual(vle[0].x.size, 9)
        self.assertEqual(speciation[0].x.size, 9)
        self.assertAlmostEqual(float(np.sum(vle[0].x)), 1.0, places=10)
        self.assertAlmostEqual(float(np.sum(speciation[0].x)), 1.0, places=10)

    def test_ionic_pressure_smoke_is_finite(self) -> None:
        target = load_vle_targets(1)[0]
        pressure = predict_co2_pressure_kPa(target.x, target.T, target.P, dict(DEFAULT_INITIAL_GUESS))
        self.assertTrue(np.isfinite(pressure))
        self.assertGreater(pressure, 0.0)


if __name__ == "__main__":
    unittest.main()
