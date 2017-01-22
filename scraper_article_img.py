#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import re

img_link = []

def getIMG(url):
	#regex magix for matching images that has og:image or twitter or facebook
	p = re.compile(ur'(?!<\w{4}\s\w{8}\S+)(?:image|twitter|facebook)"\s\w{7}\S{2}[\w\d\S]+[.jpg|.png|.gif|.jpeg|]')

	#opening site
	f = requests.get(url)

	#using regex on html code
	loot = re.findall(p, f.text)

	#adds to list
	img_link.append(loot)

	#iterates through list, and takes away shit stuff, and takes the first in the list. and returns it
	for i in img_link:
		return str(i[0]).replace('image" content="', '')

print getIMG("http://www.foxnews.com/politics/2016/05/13/conservatives-outraged-over-obama-transgender-directive-to-public-schools.html?intcmp=hpbt1")
