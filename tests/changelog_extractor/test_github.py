import unittest
from packaging_utils.changelog_extractor.changelog_extractor import convert_github

pyupgrade = {
    "url": "https://api.github.com/repos/asottile/pyupgrade/compare/v2.22.0...v2.23.1",
    "commits": [
        {
            "commit": {
                "message": "rewrite type of primitive"
            }
        }, {
            "commit": {
                "message": "test with\n\nnew\nlines"
            }
        }, {
            "commit": {
                "message": "v2.23.0"
            }
        }, {
            "commit": {
                "message": "[pre-commit.ci] pre-commit autoupdate\n\nupdates:\n- [github.com/asottile/reorder_python_imports: v2.5.0 → v2.6.0](https://github.com/asottile/reorder_python_imports/compare/v2.5.0...v2.6.0)"
            }
        }, {
            "commit": {
                "message": "Merge pull request #500 from asottile/pre-commit-ci-update-config\n\n[pre-commit.ci] pre-commit autoupdate"
            }
        }, {
            "commit": {
                "message": "fix bug in merge dicts: look for comma backwards"
            }
        }, {
            "commit": {
                "message": "Merge pull request #505 from MarcoGorelli/fix-bug-merge-dicts\n\nfix bug in merge dicts: look for comma backwards"
            }
        }, {
            "commit": {
                "message": "v2.23.1"
            }
        }
    ]
}

pyupgrade_expected = """
- update to version 2.23.1:
 - fix bug in merge dicts: look for comma backwards
- update to version 2.23.0:
 - test with
   new
   lines
 - rewrite type of primitive
""".strip()


class TestGitHub(unittest.TestCase):
    maxDiff = None

    def test_pyupgrade(self):
        self.assertEqual(convert_github((pyupgrade)),
                         pyupgrade_expected)
