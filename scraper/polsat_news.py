import logging
import math
import re
from hashlib import sha256

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from scraper.base_scraper import BaseScraper
from scraper.scrapers_exceptions import NoPagesLeftException


class PolsatNews(BaseScraper):
    """
    Class to manage PolsatNews items
    """

    def __init__(self, check_scraped_ids=True):
        super(PolsatNews, self).__init__(check_scraped_ids)
        ua = UserAgent()
        self.ua = ua.chrome
        base_items_page = BeautifulSoup(
            requests.get('https://www.polsatnews.pl/wyszukiwarka/?text=Polska&type=event',
                         headers={'User-Agent': self.ua}).text,
            'html.parser')
        PolsatNews.total_items = int(
            re.search(r"liczba wyników: (?P<count>[\d]+)", base_items_page.prettify())['count'])

        PolsatNews.items_per_page = len([article for article in base_items_page.find_all('article')])
        PolsatNews.total_pages = math.ceil(PolsatNews.total_items / PolsatNews.items_per_page)
        self.current_page = 1

    def _get_next_items(self):
        logging.debug("PolsatNews has started scraping more items...")
        if self.current_page >= PolsatNews.total_pages:
            raise NoPagesLeftException
        items_page = BeautifulSoup(requests.get(
            'https://www.polsatnews.pl/wyszukiwarka/?text=Polska&type=event&page={}'.format(self.current_page),
            headers={'User-Agent': self.ua}).text, 'html.parser')
        articles = [article for article in items_page.find_all('article')]
        items = [{'id': int(sha256(article.find('a')['href'].encode('utf-8')).hexdigest(), 16) % 10 ** 8,
                  'title': article.find('h2', {'class': 'news__title'}).text,
                  'url': article.find('a')['href'],
                  'lead': None,
                  'img': article.find('img')['data-src'],
                  'img_title': None,
                  'time_released': article.find('time')['datetime'],
                  'time_updated': None,
                  'heading': None,
                  'article_title': None,
                  'text': None,
                  'author': None} for article in articles]
        self.current_page += 1
        logging.debug("PolsatNews has finished scraping more items.")
        return items

    def _scrape_articles(self, items, delay=0.1):
        return items
