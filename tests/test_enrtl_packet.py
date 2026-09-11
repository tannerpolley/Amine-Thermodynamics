from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import runpy


VALIDATOR = runpy.run_path(Path(__file__).resolve().parents[1] / "scripts/validate_enrtl_packet.py")
PACKET_DIR = VALIDATOR["PACKET_DIR"]
RECEIPT = VALIDATOR["RECEIPT"]
load_packet = VALIDATOR["load_packet"]
validate_packet = VALIDATOR["validate_packet"]


class AdoptedPacket(unittest.TestCase):
    def copy_packet(self):
        tempdir = tempfile.TemporaryDirectory()
        root = Path(tempdir.name)
        packet = root / "packet"
        receipt = root / "receipt.json"
        shutil.copytree(PACKET_DIR, packet)
        shutil.copy(RECEIPT, receipt)
        self.addCleanup(tempdir.cleanup)
        return packet, receipt

    @staticmethod
    def refresh_hashes(packet, receipt):
        manifest_path = packet / "manifest.json"
        payload_path = packet / "payload.json"
        manifest = json.loads(manifest_path.read_text())
        payload_bytes = payload_path.read_bytes()
        for item in manifest["files"]:
            if item["path"] == "payload.json":
                item["bytes"] = len(payload_bytes)
                item["sha256"] = hashlib.sha256(payload_bytes).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        receipt_data = json.loads(receipt.read_text())
        for name, path in (("manifest.json", manifest_path), ("payload.json", payload_path)):
            content = path.read_bytes()
            receipt_data["files"][name]["bytes"] = len(content)
            receipt_data["files"][name]["sha256"] = hashlib.sha256(content).hexdigest()
        receipt_data["manifest_sha256_external"] = receipt_data["files"]["manifest.json"]["sha256"]
        receipt.write_text(json.dumps(receipt_data, indent=2) + "\n")

    def test_positive_load_and_exact_copy_contract(self):
        manifest, payload = validate_packet()
        self.assertEqual(manifest["files"][0]["path"], "payload.json")
        self.assertEqual(payload["fit"]["observation_counts"]["vle"], 240)
        self.assertEqual(
            load_packet(
                expected_model="mea-enrtl-six-parameter-corrected-dh-v1",
                expected_species_order=manifest["model"]["species_order"],
                expected_reaction_order=manifest["model"]["reaction_order"],
                expected_property_basis="true",
                expected_domain="calibration_VLE",
                result_identity="baseline-six-parameter-physical-reaction-coordinates",
            )["identity"],
            payload["identity"],
        )

    def test_changed_payload_is_rejected(self):
        packet, receipt = self.copy_packet()
        payload = packet / "payload.json"
        payload.write_bytes(payload.read_bytes() + b"\n")
        with self.assertRaises(ValueError):
            validate_packet(packet, receipt)

    def test_substituted_manifest_is_rejected(self):
        packet, receipt = self.copy_packet()
        manifest = packet / "manifest.json"
        data = json.loads(manifest.read_text())
        data["model"]["identity"] = "wrong"
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            validate_packet(packet, receipt)

    def test_semantic_tampering_is_rejected_after_hash_refresh(self):
        for case in (
            "model",
            "species",
            "reaction",
            "basis",
            "domain",
            "baseline",
            "unavailable",
            "counts",
        ):
            with self.subTest(case=case):
                packet, receipt = self.copy_packet()
                manifest_path = packet / "manifest.json"
                payload_path = packet / "payload.json"
                manifest = json.loads(manifest_path.read_text())
                payload = json.loads(payload_path.read_text())
                if case == "model":
                    manifest["model"]["identity"] = "wrong"
                elif case == "species":
                    manifest["model"]["species_order"] = ["wrong"]
                elif case == "reaction":
                    manifest["model"]["reaction_order"] = ["wrong"]
                elif case == "basis":
                    manifest["model"]["bases"]["property_basis"] = "apparent"
                elif case == "domain":
                    manifest["property_domains"]["calibration_VLE"]["loading"] = "wrong"
                elif case == "baseline":
                    payload["baseline_identity"] = "wrong"
                elif case == "unavailable":
                    manifest["unavailable_properties"].pop()
                else:
                    payload["fit"]["observation_counts"]["vle"] = 241
                manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
                payload_path.write_text(json.dumps(payload, indent=2) + "\n")
                self.refresh_hashes(packet, receipt)
                with self.assertRaises(ValueError):
                    validate_packet(packet, receipt)

    def test_non_finite_payload_is_rejected_after_hash_refresh(self):
        packet, receipt = self.copy_packet()
        payload = packet / "payload.json"
        data = json.loads(payload.read_text())
        data["parameters"][0]["value"] = float("nan")
        payload.write_text(json.dumps(data))
        self.refresh_hashes(packet, receipt)
        with self.assertRaises(ValueError):
            validate_packet(packet, receipt)

    def test_declared_boundaries_are_rejected(self):
        cases = (
            {"expected_model": "wrong"},
            {"expected_species_order": ["wrong"]},
            {"expected_reaction_order": ["wrong"]},
            {"expected_property_basis": "apparent"},
            {"expected_domain": "not-declared"},
            {"result_identity": "wrong"},
            {"requested_property": "total_reacting_solution_heat_capacity"},
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                load_packet(**kwargs)


if __name__ == "__main__":
    unittest.main()
