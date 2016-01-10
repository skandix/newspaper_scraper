# coding=utf-8
from bs4 import BeautifulSoup
from pymongo import MongoClient
from multiprocessing.pool import ThreadPool
import requests
import threading
import datetime
import time

##
# Setup
##
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
		image_meta = ""
		return image_meta


def thread_work(url):
	date = datetime.datetime.now()
	#parse url
	try:
		req = requests.get(url.get('link'), headers=request_headers)
	except:
		return None
	soup = BeautifulSoup(req.content, 'xml')

	for item in soup.findAll('item')[0:3]:
		article = {}
		article['title'] = item.title.text.encode('utf-8')
		if collection.find({'title':article.get('title')}).count() == 0:

			article['link'] = item.link.text.encode('utf-8')
			article['pubdate'] =  date.isoformat()
			article['provider'] = url.get('provider')
			article['country'] = url.get('country')
			article['category'] = url.get('category')
			try:
				article['tag'] = item.category.text.encode('utf-8')
			except:
				article['tag'] = ""
			try:
				article['image_url'] =  item.image.url.text.encode('utf-8')
			except Exception as e:
				article['image_url'] =  get_image(item.link.text.encode('utf-8'))
			print article.get('title')
			collection.insert_one(article)


def init():
	#GET urls from db
	while True:
		urls = [url for url in url_db.find({})]  #urls to parse in bjson format
		time.sleep(3)
		start = time.time()
		pool = ThreadPool(num_threads)
		pool.map(thread_work, urls)
		pool.close()
		pool.join()
		print "* Process Finished in: ", time.time() - start
		time.sleep(3)

if __name__ == '__main__':
	init()
