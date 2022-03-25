import logging
import time

from scraper.polsat_news import PolsatNews
from scraper.tvn24 import Tvn24
from scraper.tvp_info import TvpInfo

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='data/use_scrapers.log',
                    filemode='a')
logging.debug('- ' * 10 + 'use_scraper has been started ' + '- ' * 10)

tvp_scraper = TvpInfo(check_scraped_ids=True, use_database=True)
while tvp_scraper.current_page <= 2:
    tvp_scraper.scrape_more_items(scrape_articles=True, save_to_db=True, delay=0.1)
    time.sleep(1)

tvn_scraper = Tvn24(check_scraped_ids=True, use_database=True)
while tvn_scraper.current_page <= 2:
    tvn_scraper.scrape_more_items(scrape_articles=True, save_to_db=True, delay=0.1)
    time.sleep(1)

polsat_scraper = PolsatNews(check_scraped_ids=True, use_database=True)
while polsat_scraper.current_page <= 2:
    polsat_scraper.scrape_more_items(scrape_articles=True, save_to_db=True, delay=0.1)
    time.sleep(1)
