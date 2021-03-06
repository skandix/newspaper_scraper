# coding=utf-8
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from multiprocessing.pool import ThreadPool
import threading
import datetime
import time

#################################################################################################
#Variables
num_threads = 4 #number of threads
mutex = threading.Lock()

#Database
client = MongoClient('localhost', 27017)
db = client.api #name of db
url_db = db['urls']

try:
	collection = db.create_collection('articles', capped = True, max = 10000, size = 5242880)
except:
	collection = db['articles']

#Headers
request_headers = {
"Accept-Language": "en-US,en;q=0.5",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Content-Type":"Text",
"Connection": "keep-alive"
}
#################################################################################################
#This method crawls the article itself and gets the image from the facebook or twitter metatag
def get_image(url):
	try:
		req = requests.get(url, headers=request_headers)
		soup = BeautifulSoup(req.content, 'html.parser')
		image_meta = soup.find(property = 'og:image') or soup.find(name = 'twitter:image')
		return image_meta.get('content')
	except:
		return ""

#This method is handled by the thread pool.
def worker(url):
	date = datetime.datetime.now()
	#Request url
	try:
		req = requests.get(url.get('link'), headers=request_headers)
	except:
		return None

	#Soup the content
	soup = BeautifulSoup(req.content, 'xml')

	#Iter each item and parse it
	for item in soup.findAll('item')[0:3]:
		article = {}
		article['title'] = item.title.text.encode('utf-8')
		#Check if already exsists

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

			#Add to database
			mutex.acquire()
			collection.insert_one(article)
			print article.get('title')
			mutex.release()

#################################################################################################
#Init threads & urls
def init():
	#GET urls from db
	urls = [url for url in url_db.find({})]  #urls to parse in bjson format
	start = time.time()
	pool = ThreadPool(num_threads) #Create a pool of 4 worker threads
	pool.map(worker, urls) #Tell them to execute worker method
	pool.close()
	pool.join() #wait for them to finish
	print "* Process Finished in: ", time.time() - start
	threading.Timer(15, init).start()

if __name__ == '__main__':
	init()
#################################################################################################
