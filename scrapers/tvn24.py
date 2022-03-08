import json
import math
import re
import time

import requests
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from scrapers.scrapers_exceptions import NoPagesLeftException


class TVN24(BaseScraper):
    """
    Class to manage TvpInfo items
    """

    def __init__(self):
        pass

    def _get_next_items(self):
        pass

