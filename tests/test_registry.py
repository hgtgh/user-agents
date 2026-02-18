import unittest

from user_agents_updater.providers_registry import as_multi_versions, as_scalar_versions  # noqa: E402


class RegistryTests(unittest.TestCase):
    def test_as_scalar_versions_rejects_non_scalar(self):
        with self.assertRaises(RuntimeError):
            as_scalar_versions({"windows": ["145.0.7632.46"]}, "chrome")

    def test_as_multi_versions_rejects_non_list(self):
        with self.assertRaises(RuntimeError):
            as_multi_versions({"windows": "145.0.7632.46"}, "chrome")


if __name__ == "__main__":
    unittest.main()
