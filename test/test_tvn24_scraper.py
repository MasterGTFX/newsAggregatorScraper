import unittest

from scraper.tvn24 import Tvn24


class TestTvn24Scraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.scraper_base = Tvn24(check_scraped_ids=False)

        cls.scraper_with_items = Tvn24(check_scraped_ids=False)
        cls.scraper_with_items.scrape_more_items(scrape_articles=False, save_to_file=False)

        cls.scraper_with_items_and_articles = Tvn24(check_scraped_ids=False)
        cls.scraper_with_items_and_articles.scrape_more_items(scrape_articles=True, save_to_file=False)

    def test_init_base_webpage_no_exceptions(self):
        self.assertIsInstance(self.scraper_base, Tvn24)

    def test_total_pages_more_than_zero(self):
        self.assertGreater(Tvn24.total_pages, 0)

    def test_total_items_more_than_zero(self):
        self.assertGreater(Tvn24.total_items, 0)

    def test_items_per_page_more_than_zero(self):
        self.assertGreater(Tvn24.items_per_page, 0)

    def test_items_empty_before_scraping(self):
        self.assertEqual(len(self.scraper_base.items), 0)

    def test_items_available_after_scraping(self):
        self.assertGreater(len(self.scraper_with_items.items), 0)

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
            self.assertIn(field, self.scraper_with_items.items[0])

    def test_article_fields_not_available_before_scraping_article(self):
        article_field = ['img',
                         'img_title',
                         'time_released',
                         'time_updated',
                         'article_title',
                         'heading',
                         'text',
                         'author']
        for field in article_field:
            self.assertIsNone(self.scraper_with_items.items[0][field])

    def test_article_fields_not_available_after_scraping_article(self):
        article_field = ['img',
                         'img_title']
        for field in article_field:
            self.assertIsNone(self.scraper_with_items_and_articles.items[0][field])

    def test_article_fields_available_after_scraping_article(self):
        article_field = ['time_released',
                         'time_updated',
                         'article_title',
                         'heading',
                         'text',
                         'author']
        for field in article_field:
            self.assertIsNotNone(self.scraper_with_items_and_articles.items[0][field])
