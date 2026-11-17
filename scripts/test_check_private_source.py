"""Exercise the publication check against a real Git index."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import check_private_source as check


class PrivateSourceCheck(unittest.TestCase):
    def test_planted_content_paths_and_published_allowance(self):
        source = Path(check.__file__).resolve()
        published_line = next(line for line in (source.parents[1] / check.PUBLISHED_PATH).read_bytes().splitlines()
                              if hashlib.sha256(line).hexdigest() == check.PUBLISHED_LINE_HASH)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            script = root / "scripts/check_private_source.py"
            script.parent.mkdir()
            shutil.copyfile(source, script)
            published = root / check.PUBLISHED_PATH
            published.parent.mkdir(parents=True)
            published.write_bytes(published_line + b"\n")
            note = root / "note.md"
            note.write_text("Published source.\n")
            environment = {**os.environ, "PRIVATE_SOURCE_PATTERNS": json.dumps(["private-test.csv", "volatile emissions"])}

            def scan():
                subprocess.run(["git", "add", "."], cwd=root, check=True)
                return subprocess.run([sys.executable, str(script)], cwd=root, env=environment, capture_output=True)

            self.assertEqual(scan().returncode, 0)
            note.write_text("prefix-PRIVATE-TEST.CSV.git.\n")
            content = scan()
            self.assertEqual(content.returncode, 1)
            self.assertIn(b"private-source identifier", content.stderr)
            self.assertNotIn(b"private-test.csv", content.stderr.lower())
            self.assertNotIn(b"note.md", content.stderr)
            note.write_text("Published source.\n")
            private_path = root / "prefix-private-test.csv.git"
            private_path.write_text("Ordinary content.\n")
            path_result = scan()
            self.assertEqual(path_result.returncode, 1)
            self.assertIn(b"private-source identifier", path_result.stderr)
            self.assertNotIn(b"private-test.csv", path_result.stderr.lower())
            private_path.unlink()
            note.write_bytes(published_line + b"\n")
            self.assertEqual(scan().returncode, 1)  # The allowance applies only at its published path.


if __name__ == "__main__":
    unittest.main()
