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
	articles = []
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
		article['link'] = item.link.text.encode('utf-8')
		#Check if already exsists
		if collection.find(article).count() == 0:
			article['title'] = item.title.text.encode('utf-8')
			article['pubdate'] =  item.pubDate.text
			article['source'] = url.get('source')
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

			articles.append(article)

	return articles


#################################################################################################
#Init threads & urls
def init():
	#GET urls from db
	while True:
		#start = time.time()
		urls = [url for url in url_db.find({})]  #urls to parse in bjson format
		pool = ThreadPool(num_threads) #Create a pool of 4 worker threads
		articles = pool.map(worker, urls) #Tell them to execute worker method return their work
		pool.close()
		pool.join() #wait for them to finish
		for article in articles:
			if article:
				collection.insert_many(article)
				print "*"

		#print "* Process Finished in: ", time.time() - start
		time.sleep(3)


if __name__ == '__main__':
	init()
#################################################################################################
