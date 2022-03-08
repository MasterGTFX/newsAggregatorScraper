import json
import math
import re
import time

import requests
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from scrapers.scrapers_exceptions import NoPagesLeftException


class TvpInfo(BaseScraper):
    """
    Class to manage TvpInfo items
    """

    def __init__(self):
        base_items_page = BeautifulSoup(requests.get('https://www.tvp.info/polska').text, 'html.parser')
        TvpInfo.total_items = int(re.search(r"\"items_total_count\" : (?P<count>[\d]+)", base_items_page.prettify())[
                                      'count'])
        TvpInfo.items_per_page = int(re.search(r"\"items_per_page\" : (?P<count>[\d]+)", base_items_page.prettify())[
                                         'count'])
        TvpInfo.total_pages = math.ceil(TvpInfo.total_items / TvpInfo.items_per_page)
        TvpInfo.scraped_items_ids = self._get_scraped_ids()

        self.current_page = int(re.search(r"\"items_page\" : (?P<count>[\d]+)", base_items_page.prettify())['count'])
        self.items = self._get_next_items()

    def _get_next_items(self):
        if self.current_page >= TvpInfo.total_pages:
            raise NoPagesLeftException
        items_page = BeautifulSoup(requests.get('https://www.tvp.info/polska?page={}'.format(self.current_page)).text,
                                   'html.parser')
        items = json.loads(items_page.prettify().split("\"items\":")[1].split(",\n\"items_total_count\"")[0])
        self.current_page += 1
        return items
