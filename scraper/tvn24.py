import datetime
import logging
import random
import time

from bs4 import BeautifulSoup

from scraper.base_scraper import BaseScraper
from scraper.scrapers_exceptions import NoPagesLeftException


class Tvn24(BaseScraper):
    """
    Class to manage Tvn24 items
    """

    def __init__(self, check_scraped_ids=True, use_database=False):
        super(Tvn24, self).__init__(check_scraped_ids, use_database)
        base_items_page = BeautifulSoup(
            self.session.get('https://tvn24.pl/polska', headers={'User-Agent': self.ua}).text,
            'html.parser')
        Tvn24.total_items = float('inf')
        Tvn24.items_per_page = len(
            [article for article in base_items_page.find_all('article')
             if article['data-article-title']
             and article['data-article-id']
             and not '/premium/' in article.find('a')['href']
             and not '/go/programy' in article.find('a')['href']])
        Tvn24.total_pages = float('inf')
        self.current_page = 1

    def _get_next_items(self):
        logging.debug("Tvn24 has started scraping more items...")
        if self.current_page >= Tvn24.total_pages:
            raise NoPagesLeftException
        items_page = BeautifulSoup(
            self.session.get('https://tvn24.pl/polska/{}'.format(self.current_page),
                             headers={'User-Agent': self.ua}).text,
            'html.parser')
        articles = [article for article in items_page.find_all('article')
                    if article['data-article-title']
                    and article['data-article-id']
                    and not '/premium/' in article.find('a')['href']
                    and not '/go/programy' in article.find('a')['href']]
        items = [{'id': int('2' + str(article['data-article-id'])),
                  'title': article['data-article-title'],
                  'url': article.find('a')['href'],
                  'lead': article.find('div', {'class': 'article-lead'}).text if article.find('div', {
                      'class': 'article-lead'}) else None,
                  'img': None,
                  'img_title': None,
                  'time_released': None,
                  'time_updated': None,
                  'article_title': None,
                  'heading': None,
                  'text': None,
                  'source': 'Tvn24',
                  'author': None} for article in articles]
        self.current_page += 1
        logging.debug("Tvn24 has finished scraping more items.")
        return items

    def _scrape_articles(self, items, delay=0.1):
        for item in items:
            logging.debug("Tvn24 has started scraping article: {}...".format(item['title']))
            if item['id'] in self.scraped_items_ids and self.check_scraped_ids:
                logging.debug("Article already scraped, skipping.")
                continue
            item_page = BeautifulSoup(self.session.get(item['url'], headers={'User-Agent': self.ua}).text,
                                      'html.parser')
            article = item_page.find('article')
            item['time_released'] = (datetime.datetime.strptime(
                article.find('time', {'class': 'article-top-bar__date'})['datetime'].replace("Z", ""),
                '%Y-%m-%dT%H:%M:%S.%f') + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            item['time_updated'] = item['time_released']
            item['article_title'] = article.find('div',
                                                 {'class': 'article-top-bar article-top-bar--main-top-bar'}).h1.text
            item['heading'] = article.find('p', {'class': 'lead-text'}).text
            articles_part = article.find('div', {'class': 'article-story-content__elements'}).findChildren('div', {
                'class': 'article-element'})
            item['text'] = "\n".join([s for s in "\n".join(
                [paragraph.text for paragraph in articles_part[1:][:len(articles_part) - 4]]).strip().split('\n') if s])
            item['author'] = article.find('div', {'class': 'author-first-name'}).text if article.find('div', {
                'class': 'author-first-name'}) else ""
            item['img'] = article.find('img', {'class': "nuvi-player__poster"})['src'] if article.find('img', {'class': "nuvi-player__poster"}) else article.find('img', {'class': "image-component__image media-content__image"})['srcset'].split(' ')[-3].split(',')[1]
            item['img_title'] = article.find('img', {'class': "nuvi-player__poster"})['alt'] if article.find('img', {'class': "nuvi-player__poster"}) else ''
            logging.debug("Tvn24 finished scraping article.")
            time.sleep(2 * delay * random.random())
        return items


if __name__ == "__main__":
    tvn_scraper = Tvn24(check_scraped_ids=True)
    tvn_scraper.scrape_more_items(scrape_articles=True, save_to_file=False)
