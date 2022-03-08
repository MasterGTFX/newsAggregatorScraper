from scrapers.tvp_info import TvpInfo

tvp_scraper = TvpInfo()
while tvp_scraper.current_page <= 3:
    tvp_scraper.process_current_items()

