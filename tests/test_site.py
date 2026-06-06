import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.kit_items = 0
        self.quick_actions = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if attributes.get("data-kit-id"):
            self.kit_items += 1
        if tag == "button" and "quick-action" in attributes.get("class", "").split():
            self.quick_actions += 1


class SurvivalWikiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.parser = SiteParser()
        cls.parser.feed(cls.html)

    def test_version_is_2_1_0(self):
        self.assertIn('data-version="2.1.0"', self.html)

    def test_required_sections_are_present(self):
        required = {
            "water", "fire", "shelter", "navigation", "food",
            "firstaid", "signaling", "mindset", "kit", "downloads",
        }
        self.assertTrue(required.issubset(self.parser.ids))

    def test_quick_actions_cover_four_emergencies(self):
        self.assertEqual(self.parser.quick_actions, 4)
        for target in ("navigation", "firstaid", "shelter", "water"):
            self.assertRegex(self.html, rf'data-target="{target}"')

    def test_kit_has_ten_persistent_items(self):
        self.assertEqual(self.parser.kit_items, 10)
        self.assertIn("swiki-kit", self.html)
        self.assertIn('id="kit-progress-bar"', self.html)

    def test_search_and_share_features_are_wired(self):
        self.assertIn('id="search-status"', self.html)
        self.assertIn("copySectionLink", self.html)
        self.assertIn("navigator.clipboard.writeText", self.html)

    def test_compose_uses_registry_image(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("ghcr.io/specops13/survival-facts-docker:latest", compose)
        self.assertRegex(compose, r'(?m)^\s*-\s*"8080:80"\s*$')

    def test_dockerfile_copies_site_and_has_healthcheck(self):
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("COPY index.html /usr/share/nginx/html/index.html", dockerfile)
        self.assertIn("HEALTHCHECK", dockerfile)

    def test_inline_script_has_balanced_braces(self):
        script = re.search(r"<script>(.*)</script>", self.html, re.DOTALL)
        self.assertIsNotNone(script)
        source = script.group(1)
        self.assertEqual(source.count("{"), source.count("}"))


if __name__ == "__main__":
    unittest.main()
