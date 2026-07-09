from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from MEA.epcsaft_ionic.model import load_vle_targets


ROOT = Path(__file__).resolve().parents[1]
VLE_DIR = ROOT / "data" / "reference" / "MEA" / "VLE"
DATASET_PATH = VLE_DIR / "Combined_VLE.csv"
INCLUSION_PATH = VLE_DIR / "Combined_VLE_inclusion.csv"
IDRIS_PATH = VLE_DIR / "Idris_2014_VLE.csv"
GENERATOR_PATH = ROOT / "scripts" / "build_canonical_vle_dataset.py"
MANUSCRIPT_PATH = ROOT / "docs" / "latex" / "sections" / "data_methods.tex"
SOURCE_COUNTS = {
    "Aronu2011": 36,
    "Hilliard2008": 30,
    "Idris2014": 10,
    "Jou1995": 48,
    "Mamun2005": 19,
    "Xu2011": 18,
}


def _load_generator():
    spec = importlib.util.spec_from_file_location("build_canonical_vle_dataset", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load generator: {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CanonicalVLEDatasetTests(unittest.TestCase):
    def test_dataset_has_complete_six_source_provenance(self) -> None:
        dataset = pd.read_csv(DATASET_PATH)

        self.assertEqual(len(dataset), 161)
        self.assertEqual(dataset.groupby("source_key").size().to_dict(), SOURCE_COUNTS)
        self.assertEqual(dataset["row_id"].tolist(), [f"vle_{index:04d}" for index in range(1, 162)])
        self.assertFalse(dataset[["source_key", "source_file", "source_row"]].isna().any().any())
        self.assertFalse(dataset["row_id"].duplicated().any())
        self.assertFalse(dataset[["source_key", "source_row"]].duplicated().any())

    def test_idris_source_rows_are_machine_readable_and_traceable(self) -> None:
        idris = pd.read_csv(IDRIS_PATH)

        self.assertEqual(len(idris), 10)
        self.assertEqual(idris["source_row"].tolist(), list(range(1, 11)))
        self.assertEqual(set(idris["source_table_or_figure"]), {"Table 2"})
        self.assertEqual(set(idris["doi"]), {"10.1016/j.egypro.2014.11.152"})
        self.assertTrue((idris["MEA_weight_fraction"] == 0.3).all())
        self.assertTrue((idris["temperature"] == 40.0).all())

    def test_inclusion_manifest_is_complete_and_unambiguous(self) -> None:
        inclusion = pd.read_csv(INCLUSION_PATH)

        self.assertEqual(len(inclusion), 161)
        self.assertEqual(inclusion["sequence"].tolist(), list(range(1, 162)))
        self.assertFalse(inclusion[["source_key", "source_file", "source_row"]].isna().any().any())
        self.assertFalse(inclusion[["source_key", "source_row"]].duplicated().any())

    def test_model_targets_retain_canonical_identity(self) -> None:
        targets = load_vle_targets()

        self.assertEqual(len(targets), 161)
        self.assertEqual({target.source_key for target in targets}, set(SOURCE_COUNTS))
        self.assertEqual({target.row_id for target in targets}, {f"vle_{index:04d}" for index in range(1, 162)})

    def test_generator_reproduces_the_tracked_dataset_byte_for_byte(self) -> None:
        module = _load_generator()
        with tempfile.TemporaryDirectory() as temporary_directory:
            generated_path = Path(temporary_directory) / "Combined_VLE.csv"
            module.build_dataset(output_path=generated_path)
            first_build = generated_path.read_bytes()
            module.build_dataset(output_path=generated_path)

            self.assertEqual(first_build, generated_path.read_bytes())
            self.assertEqual(DATASET_PATH.read_bytes(), generated_path.read_bytes())

    def test_manuscript_declares_all_six_vle_sources(self) -> None:
        manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("six VLE sources", manuscript)
        self.assertIn("Idris2014", manuscript)


if __name__ == "__main__":
    unittest.main()
