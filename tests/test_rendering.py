import unittest

from user_agents_updater.models import UARenderVariantDTO  # noqa: E402
from user_agents_updater.rendering import render_variants  # noqa: E402


class RenderingTests(unittest.TestCase):
    def test_render_variants_supports_scalar_and_multi_versions(self):
        variants = [
            UARenderVariantDTO(
                platform="desktop",
                os="windows",
                token="Windows NT 10.0; Win64; x64",
                template="Mozilla/5.0 ({token}) Chrome/{version}",
            ),
            UARenderVariantDTO(
                platform="desktop",
                os="macos",
                token="Macintosh; Intel Mac OS X 10_15_7",
                template="Mozilla/5.0 ({token}) Chrome/{major_version}.0.0.0",
            ),
        ]
        rendered = render_variants(
            browser="chrome",
            variants=variants,
            versions_by_os={
                "windows": "145.0.7632.46",
                "macos": ["145.0.7632.45", "144.0.7559.132"],
            },
        )

        self.assertEqual(len(rendered), 3)
        self.assertEqual(rendered[0].browser_major_version, "145")
        self.assertIn("Chrome/145.0.7632.46", rendered[0].user_agent)
        self.assertIn("Chrome/145.0.0.0", rendered[1].user_agent)
        self.assertIn("Chrome/144.0.0.0", rendered[2].user_agent)


if __name__ == "__main__":
    unittest.main()
