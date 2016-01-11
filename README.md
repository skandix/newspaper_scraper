# newspaper_scraper
Scraping any newspaper with help of RSS feed

###scraper.py
Older version which does not benefit threading, which also means longer execution time for a set of URLs.
Use this version if you don't care about speed, but CPU load.
*Benchmark (22 urls): 18.4719998837 s

###scraper_threaded.py
Using threads to split work. Faster execution time, but more CPU load. Recommended.
*Benchmark (22 urls): 6.63800001144 s

####scraper_feed.py
Using feedparser library instead to parse each RSS feed from the URL. Cleaner, but not faster.
* Benchmark (22 urls): 9.14100003242 s
