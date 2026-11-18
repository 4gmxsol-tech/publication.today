import tempfile
import unittest
from pathlib import Path
from inject_ads import TAG, inject_ads


class ArticleAdInjectionTests(unittest.TestCase):
    def make_site(self, root):
        (root / "assets" / "js").mkdir(parents=True)
        (root / "assets" / "js" / "adsterra-ads.js").write_text("/* consent gate */", encoding="utf-8")
        pages = {
            "articles/one.html": "<html><body><article>Story</article></body></html>",
            "articles/two.html": '<html><body><script src="/assets/js/adsterra-ads.js" defer></script></body></html>',
            "articles/index.html": "<html><body>Archive</body></html>",
        }
        for name, value in pages.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")

    def test_injects_missing_article_once_and_skips_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_site(root)
            self.assertEqual(inject_ads(root), (1, 2))
            one = (root / "articles/one.html").read_text(encoding="utf-8")
            two = (root / "articles/two.html").read_text(encoding="utf-8")
            archive = (root / "articles/index.html").read_text(encoding="utf-8")
            self.assertEqual(one.count(TAG), 1)
            self.assertEqual(two.count(TAG), 1)
            self.assertNotIn(TAG, archive)
            self.assertEqual(inject_ads(root), (0, 2))

    def test_fails_if_controller_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "articles").mkdir()
            with self.assertRaisesRegex(ValueError, "controller is missing"):
                inject_ads(root)

    def test_fails_if_article_has_no_body_close(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets/js").mkdir(parents=True)
            (root / "assets/js" / "adsterra-ads.js").write_text("/* consent gate */", encoding="utf-8")
            (root / "articles").mkdir()
            (root / "articles/broken.html").write_text("<html>broken</html>", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Missing </body>"):
                inject_ads(root)


if __name__ == "__main__":
    unittest.main()
