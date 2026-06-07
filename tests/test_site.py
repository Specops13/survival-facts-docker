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
        self.knot_diagrams = 0
        self.knot_names = set()
        self.three_step_knots = 0
        self.knot_photos = 0
        self.reference_photos = 0
        self.reference_categories = set()
        self.topic_headings = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if attributes.get("data-kit-id"):
            self.kit_items += 1
        if tag == "button" and "quick-action" in attributes.get("class", "").split():
            self.quick_actions += 1
        if tag == "svg" and "knot-diagram" in attributes.get("class", "").split():
            self.knot_diagrams += 1
            if attributes.get("data-knot"):
                self.knot_names.add(attributes["data-knot"])
            if attributes.get("data-knot-steps") == "3":
                self.three_step_knots += 1
        if tag == "figure" and "knot-photo" in attributes.get("class", "").split():
            self.knot_photos += 1
        if tag == "figure" and "reference-photo" in attributes.get("class", "").split():
            self.reference_photos += 1
            if attributes.get("data-reference-category"):
                self.reference_categories.add(attributes["data-reference-category"])
        if tag == "h3":
            self.topic_headings += 1


class SurvivalWikiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.parser = SiteParser()
        cls.parser.feed(cls.html)

    def test_version_is_3_2_0(self):
        self.assertIn('data-version="3.2.0"', self.html)

    def test_required_sections_are_present(self):
        required = {
            "water", "fire", "shelter", "navigation", "food",
            "firstaid", "signaling", "mindset", "weather", "vehicle",
            "knots", "tools", "kit", "downloads",
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

    def test_fast_search_and_share_features_are_wired(self):
        self.assertIn('id="quick-search"', self.html)
        self.assertIn('id="search-results-list"', self.html)
        self.assertIn("searchTopics", self.html)
        self.assertIn("selectedSearchResult", self.html)
        self.assertGreaterEqual(self.parser.topic_headings, 55)
        self.assertIn("copySectionLink", self.html)
        self.assertIn("navigator.clipboard.writeText", self.html)

    def test_knot_diagrams_and_tools_are_present(self):
        self.assertEqual(self.parser.knot_diagrams, 4)
        self.assertEqual(self.parser.three_step_knots, 4)
        self.assertEqual(self.parser.knot_photos, 4)
        self.assertEqual(
            self.parser.knot_names,
            {"figure-eight", "bowline", "taut-line", "clove-hitch"},
        )
        self.assertEqual(self.html.count('class="knot-check"'), 4)
        self.assertEqual(self.html.count('class="knot-photo"'), 4)
        self.assertIn("inlineLocalImages", self.html)
        for filename in (
            "figure-eight-real-world.jpg",
            "bowline-real-world.jpg",
            "taut-line-real-world.jpg",
            "clove-hitch-real-world.jpg",
        ):
            self.assertTrue((ROOT / "assets" / "knots" / filename).is_file())
        self.assertIn("Clove_Hitch_-_ABoK_11_-_USCG.jpg", self.html)
        self.assertIn("CC0 public domain dedication", self.html)
        for knot in ("Figure-Eight Stopper", "Bowline", "Taut-Line Hitch", "Clove Hitch"):
            self.assertIn(knot, self.html)
        for tool_id in ("planner-condition", "planner-result", "water-people", "water-result"):
            self.assertIn(f'id="{tool_id}"', self.html)

    def test_category_reference_photos_are_local_and_attributed(self):
        expected = {
            "water": "water-purification.jpg",
            "fire": "campfire.jpg",
            "shelter": "lean-to-shelter.jpg",
            "navigation": "map-compass.jpg",
            "firstaid": "medical-kit.jpg",
            "signaling": "signal-mirror.jpg",
            "weather": "lightning.jpg",
            "vehicle": "vehicle-kit.jpg",
        }
        self.assertEqual(self.parser.reference_photos, len(expected))
        self.assertEqual(self.parser.reference_categories, set(expected))
        self.assertEqual(self.html.count('class="reference-photo"'), len(expected))
        self.assertGreaterEqual(self.html.count("public domain"), len(expected))
        for filename in expected.values():
            self.assertTrue((ROOT / "assets" / "references" / filename).is_file())
            self.assertIn(f"assets/references/{filename}", self.html)

    def test_compose_uses_registry_image(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("ghcr.io/specops13/survival-facts-docker:latest", compose)
        self.assertRegex(compose, r'(?m)^\s*-\s*"8080:80"\s*$')

    def test_dockerfile_copies_site_and_has_healthcheck(self):
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("COPY index.html /usr/share/nginx/html/index.html", dockerfile)
        self.assertIn("COPY assets /usr/share/nginx/html/assets", dockerfile)
        self.assertIn("HEALTHCHECK", dockerfile)

    def test_inline_script_has_balanced_braces(self):
        script = re.search(r"<script>(.*)</script>", self.html, re.DOTALL)
        self.assertIsNotNone(script)
        source = script.group(1)
        self.assertEqual(source.count("{"), source.count("}"))


if __name__ == "__main__":
    unittest.main()
