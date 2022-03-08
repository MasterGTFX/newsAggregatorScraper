import json
import os


class BaseScraper:
    """
    Class to manage TvpInfo items
    """
    total_items = 0
    items_per_page = 0
    total_pages = 0
    scraped_items_ids = []

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, value):
        self._items = [item for item in value if item['id'] not in self.__class__.scraped_items_ids]
        self.__class__.scraped_items_ids.extend([item['id'] for item in self.items])

    def process_current_items(self):
        self.items = self._get_next_items()
        self._save_to_file()

    def _get_next_items(self):
        raise NotImplementedError

    def _get_scraped_ids(self):
        try:
            with open(os.path.join('data', self.__class__.__name__ + '.json'), 'r') as json_items_file:
                items = json.load(json_items_file)
                ids = [item['id'] for item in items]
            return ids
        except FileNotFoundError:
            return []

    def _save_to_file(self):
        try:
            with open(os.path.join('data', self.__class__.__name__ + '.json'), 'r') as input_file:
                items = json.load(input_file)
                items.extend(self.items)
        except FileNotFoundError:
            items = self.items
        with open(os.path.join('data', self.__class__.__name__ + '.json'), 'w') as output_file:
            json.dump(items, output_file)
        self.__class__.scraped_items_ids = self._get_scraped_ids()
