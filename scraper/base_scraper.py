import json
import logging
import os
from contextlib import contextmanager

import psycopg2
import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter, Retry

from scraper.scrapers_exceptions import DatabaseConnectionNotInitialized


# postgres:postgres:5432
class BaseScraper:
    """
    Class to manage TvpInfo items
    """
    total_items = 0
    items_per_page = 0
    total_pages = 0
    scraped_items_ids = []

    def __init__(self, check_scraped_ids, use_database):
        self.check_scraped_ids = check_scraped_ids
        self.use_database = use_database
        self._items = []
        if check_scraped_ids:
            self.scraped_items_ids = self._get_scraped_ids()
        ua = UserAgent()
        self.ua = ua.chrome
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 501, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        logging.debug(self.__class__.__name__ + " scraper has been initialized.")

    @contextmanager
    def database(self):
        db_conn = psycopg2.connect(
            host=os.getenv("db_host"),
            database=os.getenv("db_name"),
            user=os.getenv("db_user"),
            password=os.getenv("db_pass"),
            port=os.getenv("db_port"))
        db_cursor = db_conn.cursor()
        try:
            yield db_cursor
        finally:
            db_conn.commit()
            db_cursor.close()
            db_conn.close()

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, value):
        if self.check_scraped_ids and self.scraped_items_ids:
            self._items = [item for item in value if item['id'] not in self.scraped_items_ids]
        else:
            self._items = value
        self.scraped_items_ids.extend([item['id'] for item in self.items])

    def scrape_more_items(self, scrape_articles=True, save_to_file=False, save_to_db=False, delay=0.1):
        self.items = self._get_next_items() if not scrape_articles else self._scrape_articles(self._get_next_items(),
                                                                                              delay)
        if save_to_file:
            self._save_to_file()

        if save_to_db:
            if not self.use_database:
                raise DatabaseConnectionNotInitialized
            self._save_to_db()

    def _get_next_items(self):
        raise NotImplementedError

    def _scrape_articles(self, items, delay):
        raise NotImplementedError

    def _get_scraped_ids(self):
        if not self.use_database:
            try:
                with open(os.path.join('data', self.__class__.__name__ + '.json'), 'r',
                          encoding='utf8') as json_items_file:
                    items = json.load(json_items_file)
                    ids = [item['id'] for item in items]
                    logging.debug(self.__class__.__name__ + " scraped ids: " + repr(ids))
                return ids
            except FileNotFoundError:
                logging.debug(self.__class__.__name__ + " has no already scraped ids (FileNotFound)")
                return []
        else:
            with self.database() as cursor:
                try:
                    cursor.execute('SELECT id FROM articles_article WHERE source=\'{}\';'.format(self.__class__.__name__))
                    ids = [item[0] for item in cursor.fetchall()]
                    return ids
                except psycopg2.ProgrammingError as err:
                    logging.debug(self.__class__.__name__ + " has no already scraped ids in databse (ProgrammingError)")
            return []

    def _save_to_file(self):
        try:
            with open(os.path.join('data', self.__class__.__name__ + '.json'), 'r', encoding='utf8') as input_file:
                items = json.load(input_file)
                items.extend(self.items)
                logging.debug(self.__class__.__name__ + " new items: " + repr(self.items))
        except FileNotFoundError:
            items = self.items
        with open(os.path.join('data', self.__class__.__name__ + '.json'), 'w', encoding='utf8') as output_file:
            json.dump(items, output_file, ensure_ascii=False)
        self.scraped_items_ids = self._get_scraped_ids()
        logging.debug(self.__class__.__name__ + " items has been save to " +
                      os.path.join('data', self.__class__.__name__ + '.json'))

    def _save_to_db(self):
        with self.database() as cursor:
            for item in self.items:
                cursor.execute('INSERT INTO articles_article (id, title, url, lead, img, img_title,time_released, '
                               'time_updated, heading, article_title, text, author, source) '
                               'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                               (item['id'], item['title'], item['url'], item['lead'], item['img'], item['img_title'],
                                item['time_released'], item['time_updated'], item['heading'], item['article_title'],
                                item['text'], item['author'], item['source']))
        self.scraped_items_ids = self._get_scraped_ids()
        logging.debug(self.__class__.__name__ + " items has been save to database")


if __name__ == "__main__":
    scraper = BaseScraper(check_scraped_ids=True, use_database=False)
    print(scraper._get_scraped_ids())
