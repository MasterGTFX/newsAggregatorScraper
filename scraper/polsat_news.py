import datetime
import logging
import math
import re
from hashlib import sha256

from bs4 import BeautifulSoup

from scraper.base_scraper import BaseScraper
from scraper.scrapers_exceptions import NoPagesLeftException


class PolsatNews(BaseScraper):
    """
    Class to manage PolsatNews items
    """

    def __init__(self, check_scraped_ids=True):
        super(PolsatNews, self).__init__(check_scraped_ids)
        base_items_page = BeautifulSoup(
            self.session.get('https://www.polsatnews.pl/wyszukiwarka/?text=Polska&type=event',
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
        items_page = BeautifulSoup(self.session.get(
            'https://www.polsatnews.pl/wyszukiwarka/?text=Polska&type=event&page={}'.format(self.current_page),
            headers={'User-Agent': self.ua}).text, 'html.parser')
        articles = [article for article in items_page.find_all('article')]
        items = [{'id': int(sha256(article.find('a')['href'].encode('utf-8')).hexdigest(), 16) % 10 ** 8,
                  'title': article.find('h2', {'class': 'news__title'}).text,
                  'url': article.find('a')['href'],
                  'lead': None,
                  'img': article.find('img')['data-src'],
                  'img_title': None,
                  'time_released': datetime.datetime.strptime(article.find('time')['datetime'],
                                                              "%Y-%m-%d %H:%M").strftime('%Y-%m-%d %H:%M:%S'),
                  'time_updated': datetime.datetime.strptime(article.find('time')['datetime'],
                                                             "%Y-%m-%d %H:%M").strftime('%Y-%m-%d %H:%M:%S'),
                  'heading': None,
                  'article_title': None,
                  'text': None,
                  'author': None} for article in articles]
        self.current_page += 1
        logging.debug("PolsatNews has finished scraping more items.")
        return items

    def _scrape_articles(self, items, delay=0.1):
        for item in items:
            logging.debug("PolsatNews has started scraping article: {}...".format(item['title']))
            if item['id'] in self.scraped_items_ids and self.check_scraped_ids:
                logging.debug("Article already scraped, skipping.")
                continue
            item_page = BeautifulSoup(self.session.get(item['url'], headers={'User-Agent': self.ua}).text, 'html.parser')
            article = item_page.find('article')
            item['img_title'] = article.find('img', {'class': 'news__img'})['alt']
            item['heading'] = article.find('div', {'class': 'news__preview'}).text
            item['lead'] = item['heading']
            item['article_title'] = article.find('h1', {'class': 'news__title'}).text
            item['author'] = article.find('div', {'class': 'news__author'}).text
            item['text'] = "\n".join([paragraph.text.strip() for paragraph in
                                      article.find('div', {'class': 'news__description'}).find_all(
                                          re.compile('p|h2'), recursive=False) if
                                      not paragraph.a and paragraph.text.strip()]).strip()
            logging.debug("PolsatNews finished scraping article.")
        return items


if __name__ == "__main__":
    polsat_scraper = PolsatNews(check_scraped_ids=True)
    polsat_scraper.scrape_more_items(scrape_articles=True, save_to_file=False)
