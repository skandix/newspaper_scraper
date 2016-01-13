import scraper_bulk
import daemon

with daemon.DaemonContext():
    instance = scraper_bulk()
