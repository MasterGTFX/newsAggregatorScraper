import json
import os
import re

import requests
from bs4 import BeautifulSoup


def get_tvp_info_news():
    base_news_page = BeautifulSoup(requests.get('https://www.tvp.info/polska').text, 'html.parser')
    items = json.loads(base_news_page.prettify().split("\"items\":")[1].split(",\n\"items_total_count\"")[0])
    items_total_count = re.search(r"\"items_total_count\" : (?P<count>[\d]+)", base_news_page.prettify())['count']
    items_per_page = re.search(r"\"items_per_page\" : (?P<count>[\d]+)", base_news_page.prettify())['count']
    items_page = re.search(r"\"items_page\" : (?P<count>[\d]+)", base_news_page.prettify())['count']

    with open(os.path.join(os.pardir, 'data', 'tvp_info.json'), 'w') as outfile:
        json.dump(items, outfile)


get_tvp_info_news()
