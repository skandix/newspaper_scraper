# newspaper_scraper
Scraping any newspaper with help of RSS feed. Also retrieves image url from the article itself.

***Using 4 threads***
##scraper.py
Single threaded version which does not benefit threading, which also means longer execution time for a set of URLs.
Use this version if you don't care about speed, but CPU load.
* Benchmark (22 urls): 18.4719998837 s

##scraper_threaded.py
Using threads to split work. Faster execution time, but more CPU load.
* Benchmark (22 urls): 6.63800001144 s

###scraper_feed.py
Using feedparser library instead to parse each RSS feed from the URL. Cleaner, but not faster.
* Benchmark (22 urls): 9.14100003242 s

###scraper_bulk.py
Instead of adding each article instantly to the database. We are first gathering all of it, and when all the the threads are done, we simply pass all the articles at once. This does not hurt the database, and still is efficent.
* Benchmark (22 urls): 6.438125643912 s
