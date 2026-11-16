"""Protect identifier detection at publication boundaries."""
import unittest
from unittest.mock import patch

import check_private_source as check


class PrivateSourceCheck(unittest.TestCase):
    def test_punctuation_and_paths(self):
        identifier = "private-test.csv"
        with patch.object(check, "patterns", return_value=(identifier,)):
            self.assertTrue(list(check.violations("note.md", (identifier + ".").encode())))
            self.assertTrue(list(check.violations("folder/" + identifier, b"ordinary content")))
            self.assertTrue(list(check.violations("folder/" + identifier + ".git", b"ordinary")))
            self.assertTrue(list(check.violations("note.md", (identifier + ".git").encode())))
            self.assertTrue(check.path_is_blocked("prefix-" + identifier + "-suffix"))
            self.assertFalse(list(check.violations("note.md", b"published source")))


if __name__ == "__main__":
    unittest.main()
