import unittest

from user_agents_updater.models import ResolvedVersionsDTO  # noqa: E402


class ModelsTests(unittest.TestCase):
    def test_resolved_versions_round_trip_and_immutability(self):
        resolved = ResolvedVersionsDTO.from_mapping(
            {
                "chrome": {"windows": ["145.0.7632.46", "144.0.7559.132"]},
                "edge": {"windows": "144.0.3719.115"},
            }
        )

        chrome_versions = resolved.versions_for("chrome")
        chrome_versions["windows"].append("143.0.7499.40")

        self.assertEqual(
            resolved.versions_for("chrome")["windows"],
            ["145.0.7632.46", "144.0.7559.132"],
        )
        self.assertEqual(resolved.to_dict()["edge"]["windows"], "144.0.3719.115")

    def test_resolved_versions_from_mapping_rejects_empty_input(self):
        with self.assertRaises(RuntimeError):
            ResolvedVersionsDTO.from_mapping({})


if __name__ == "__main__":
    unittest.main()
