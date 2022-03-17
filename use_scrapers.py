import logging
import time

from scrapers.polsat_news import PolsatNews
from scrapers.tvn24 import Tvn24
from scrapers.tvp_info import TvpInfo

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='data/use_scrapers.log',
                    filemode='a')
logging.debug('- ' * 10 + 'use_scraper has been started ' + '- ' * 10)

tvp_scraper = TvpInfo()
while tvp_scraper.current_page <= 2:
    tvp_scraper.process_current_items()
    time.sleep(1)

tvn_scraper = Tvn24()
while tvn_scraper.current_page <= 2:
    tvn_scraper.process_current_items()
    time.sleep(1)

polsat_scraper = PolsatNews()
while polsat_scraper.current_page <= 2:
    polsat_scraper.process_current_items()
    time.sleep(1)
