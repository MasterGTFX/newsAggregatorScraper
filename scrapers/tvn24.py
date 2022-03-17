import requests
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from scrapers.scrapers_exceptions import NoPagesLeftException


class Tvn24(BaseScraper):
    """
    Class to manage Tvn24 items
    """

    def __init__(self):
        BaseScraper.__init__(self)
        base_items_page = BeautifulSoup(requests.get('https://tvn24.pl/polska').text, 'html.parser')
        Tvn24.total_items = float('inf')
        Tvn24.items_per_page = len(
            [article for article in base_items_page.find_all('article') if article['data-article-title']])
        Tvn24.total_pages = float('inf')
        Tvn24.scraped_items_ids = self._get_scraped_ids()
        self.current_page = 1
        self.process_current_items()

    def _get_next_items(self):
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
                  'time_updated': None} for article in articles]
        self.current_page += 1
        return items
