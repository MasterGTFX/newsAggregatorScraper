import json
import logging
import os


class BaseScraper:
    """
    Class to manage TvpInfo items
    """
    total_items = 0
    items_per_page = 0
    total_pages = 0
    scraped_items_ids = []

    def __init__(self, check_scraped_ids):
        self._items = []
        self.check_scraped_ids = check_scraped_ids
        if check_scraped_ids:
            self.scraped_items_ids = self._get_scraped_ids()
        logging.debug(self.__class__.__name__ + " scraper has been initialized.")

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

    def scrape_more_items(self, scrape_articles=True, save_to_file=False, delay=0.1):
        self.items = self._get_next_items() if not scrape_articles else self._scrape_articles(self._get_next_items(),
                                                                                              delay)
        if save_to_file:
            self._save_to_file()

    def _get_next_items(self):
        raise NotImplementedError

    def _scrape_articles(self, items, delay):
        raise NotImplementedError

    def _get_scraped_ids(self):
        try:
            with open(os.path.join('data', self.__class__.__name__ + '.json'), 'r') as json_items_file:
                items = json.load(json_items_file)
                ids = [item['id'] for item in items]
                logging.debug(self.__class__.__name__ + " scraped ids: " + repr(ids))
            return ids
        except FileNotFoundError:
            logging.debug(self.__class__.__name__ + " has no already scraped ids (FileNotFound)")
            return []

    def _save_to_file(self):
        try:
            with open(os.path.join('data', self.__class__.__name__ + '.json'), 'r') as input_file:
                items = json.load(input_file)
                items.extend(self.items)
                logging.debug(self.__class__.__name__ + " new items: " + repr(self.items))
        except FileNotFoundError:
            items = self.items
        with open(os.path.join('data', self.__class__.__name__ + '.json'), 'w') as output_file:
            json.dump(items, output_file)
        self.scraped_items_ids = self._get_scraped_ids()
        logging.debug(self.__class__.__name__ + " items has been save to " +
                      os.path.join('data', self.__class__.__name__ + '.json'))