import json
import logging
import math
import random
import re
import time
from datetime import datetime

from bs4 import BeautifulSoup

from scraper.base_scraper import BaseScraper
from scraper.scrapers_exceptions import NoPagesLeftException


class TvpInfo(BaseScraper):
    """
    Class to manage TvpInfo items
    """

    def __init__(self, check_scraped_ids=True, use_database=False):
        super(TvpInfo, self).__init__(check_scraped_ids, use_database)
        base_items_page = BeautifulSoup(
            self.session.get('https://www.tvp.info/polska', headers={'User-Agent': self.ua}).text, 'html.parser')
        TvpInfo.total_items = int(re.search(r"\"items_total_count\" : (?P<count>[\d]+)", base_items_page.prettify())[
                                      'count'])
        TvpInfo.items_per_page = int(re.search(r"\"items_per_page\" : (?P<count>[\d]+)", base_items_page.prettify())[
                                         'count'])
        TvpInfo.total_pages = math.ceil(TvpInfo.total_items / TvpInfo.items_per_page)
        self.current_page = int(re.search(r"\"items_page\" : (?P<count>[\d]+)", base_items_page.prettify())['count'])

    def _get_next_items(self):
        logging.debug("TvpInfo has started scraping more items...")
        if self.current_page >= TvpInfo.total_pages:
            raise NoPagesLeftException
        items_page = BeautifulSoup(self.session.get('https://www.tvp.info/polska?page={}'.format(self.current_page), headers={'User-Agent': self.ua}).text,
                                   'html.parser')
        items = json.loads(items_page.prettify().split("\"items\":")[1].split(",\n\"items_total_count\"")[0])
        items = [{'id': item['id'],
                  'title': item['title'],
                  'url': 'https://www.tvp.info' + item['url'],
                  'lead': item['lead'],
                  'img': item['image']['url'],
                  'img_title': item['image']['title'],
                  'time_released': datetime.fromtimestamp(int(item['publication_start'])/1000).strftime('%Y-%m-%d %H:%M:%S'),
                  'time_updated': datetime.fromtimestamp(int(item['release_date'])/1000).strftime('%Y-%m-%d %H:%M:%S'),
                  'article_title': None,
                  'heading': None,
                  'text': None,
                  'source': "TvpInfo",
                  'author': None} for item in items]
        self.current_page += 1
        logging.debug("TvpInfo has finished scraping more items.")
        return items

    def _scrape_articles(self, items, delay=0.1):
        for item in items:
            logging.debug("TvpInfo has started scraping article: {}...".format(item['title']))
            if item['id'] in self.scraped_items_ids and self.check_scraped_ids:
                logging.debug("Article already scraped, skipping.")
                continue
            item_page = BeautifulSoup(self.session.get(item['url'], headers={'User-Agent': self.ua}).text, 'html.parser')
            item['article_title'] = item_page.find('div', {"class": 'layout-article'}).h1.text
            item['author'] = item_page.find('div', {"class": 'info-article__date'}).span.text
            item['heading'] = item_page.find('p', {"class": 'am-article__heading article__width'}).b.text
            item['text'] = "\n".join(
                [s for s in "".join([article_part.text for article_part in item_page.find_all('p', {
                    "class": 'am-article__text article__width'})]).strip().split("\n") if s]).replace(
                '#wieszwiecejPolub nas', '')
            logging.debug("TvpInfo finished scraping article.")
            time.sleep(2 * delay * random.random())
        return items


if __name__ == "__main__":
    tvp_scraper = TvpInfo(check_scraped_ids=True, use_database=True)
    tvp_scraper.scrape_more_items(scrape_articles=True, save_to_db=True)
