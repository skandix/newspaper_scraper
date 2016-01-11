from multiprocessing.pool import ThreadPool
from pymongo import MongoClient
from bs4 import BeautifulSoup
import feedparser
import pprint
import requests
import time

#################################################################################################
num_threads = 4
client = MongoClient('localhost', 27017)
db = client.api #name of db
url_db = db['urls']

try:
	collection = db.create_collection('articles', capped = True, max = 3000, size = 5242880)
except:
	collection = db['articles']

request_headers = {
"Accept-Language": "en-US,en;q=0.5",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Content-Type":"Text",
"Connection": "keep-alive"
}
#################################################################################################
def get_image(url):
	try:
		req = requests.get(url, headers=request_headers)
		soup = BeautifulSoup(req.content, 'html.parser')
		image_meta = soup.find(property = 'og:image') or soup.find(name = 'twitter:image')
		return image_meta.get('content')
	except:
		return ""


def worker(url):
	feed = feedparser.parse(url.get('link'))
	items = feed['items']
	for item in items[0:3]:
		article = {}
		article['title'] = item['title'].encode('utf-8')
		if collection.find({'title':article.get('title')}).count() == 0:
			article['date'] = item['published'].encode('utf-8')
			article['provider'] = url.get('provider')
			article['country'] = url.get('country')
			article['category'] = url.get('category')
			article['image_url'] = get_image(item['link'])
			collection.insert_one(article)
			print article.get('title')



def init():
	while True:
		start = time.time()
		urls = [url for url in url_db.find({})]
		print "Process started with %s urls" % len(urls)
		pool = ThreadPool(num_threads)
		pool.map(worker, urls)
		pool.close()
		pool.join()
		print "-----------"
		print "Process finished in: %s" % (time.time() - start)
		time.sleep(3)

if __name__ == '__main__':
	init()
