import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from scraper.base_scraper import BaseScraper
from scraper.scrapers_exceptions import NoPagesLeftException


class Tvn24(BaseScraper):
    """
    Class to manage Tvn24 items
    """

    def __init__(self, check_scraped_ids=True):
        super(Tvn24, self).__init__(check_scraped_ids)
        base_items_page = BeautifulSoup(requests.get('https://tvn24.pl/polska').text, 'html.parser')
        Tvn24.total_items = float('inf')
        Tvn24.items_per_page = len(
            [article for article in base_items_page.find_all('article') if article['data-article-title']])
        Tvn24.total_pages = float('inf')
        self.current_page = 1

    def _get_next_items(self):
        logging.debug("Tvn24 has started scraping more items...")
        if self.current_page >= Tvn24.total_pages:
            raise NoPagesLeftException
        items_page = BeautifulSoup(requests.get('https://tvn24.pl/polska/{}'.format(self.current_page)).text,
                                   'html.parser')
        articles = [article for article in items_page.find_all('article') if article['data-article-title']]
        items = [{'id': article['data-article-id'],
                  'title': article['data-article-title'],
                  'url': article.find('a')['href'],
                  'lead': None,
                  'img': None,
                  'img_title': None,
                  'time_released': None,
                  'time_updated': None,
                  'article_title': None,
                  'heading': None,
                  'text': None,
                  'author': None} for article in articles]
        self.current_page += 1
        logging.debug("Tvn24 has finished scraping more items.")
        return items

    def _scrape_articles(self, items, delay=0.1):
        return items