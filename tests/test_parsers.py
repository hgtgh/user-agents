import unittest

from user_agents_updater.parsers import major_version, parse_semver_like  # noqa: E402


class ParsersTests(unittest.TestCase):
    def test_parse_semver_like_returns_tuple_for_numeric_version(self):
        self.assertEqual(parse_semver_like("145.0.7632.46"), (145, 0, 7632, 46))

    def test_parse_semver_like_returns_empty_tuple_for_non_numeric_version(self):
        self.assertEqual(parse_semver_like("145.0-beta"), ())

    def test_major_version_returns_first_segment(self):
        self.assertEqual(major_version("145.0.7632.46"), "145")


if __name__ == "__main__":
    unittest.main()
