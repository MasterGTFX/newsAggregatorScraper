import unittest

from scraper.base_scraper import BaseScraper


class TestBaseScraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.scraper_base = BaseScraper(check_scraped_ids=False)

    def test_scraper_request_session_is_working(self):
        r = self.scraper_base.session.get("https://google.com")
        self.assertIs(r.status_code, 200)

    def test_get_items_raises_error_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.scraper_base._get_next_items()

    def test_get_articles_raises_error_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.scraper_base._scrape_articles([], 1)
