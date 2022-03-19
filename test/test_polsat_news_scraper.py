import unittest

from scraper.polsat_news import PolsatNews


class TestPolsatNewsScraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.scraper_base = PolsatNews(check_scraped_ids=False)

        cls.scraper_items = PolsatNews(check_scraped_ids=False)
        cls.scraper_items.scrape_more_items(scrape_articles=False, save_to_file=False)

    def test_init_base_webpage_no_exceptions(self):
        self.assertIsInstance(self.scraper_base, PolsatNews)

    def test_total_pages_more_than_zero(self):
        self.assertGreater(PolsatNews.total_pages, 0)

    def test_total_items_more_than_zero(self):
        self.assertGreater(PolsatNews.total_items, 0)

    def test_items_per_page_more_than_zero(self):
        self.assertGreater(PolsatNews.items_per_page, 0)

    def test_items_empty_before_scraping(self):
        self.assertEqual(len(self.scraper_base.items), 0)

    def test_items_available_after_scraping(self):
        self.assertGreater(len(self.scraper_items.items), 0)

    def test_items_have_all_required_fields(self):
        fields = ['id',
                  'title',
                  'url',
                  'lead',
                  'img',
                  'img_title',
                  'time_released',
                  'time_updated',
                  'article_title',
                  'heading',
                  'text',
                  'author']
        for field in fields:
            self.assertIn(field, self.scraper_items.items[0])