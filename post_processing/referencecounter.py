import re
import datetime
import codecs
import json
import page_parser
import sys
import pdb

import time

pages = []
lastContentId = 0

start = 0

linksPattern = re.compile('\[\[(.*?)(?:\|.*?)?\]\]')

def contentHandler(content):
	#not too sure why we need the globals in here...
	#it might have to do with this function being a callback
	global lastContentId
	global pages

	#so that we know where we left off
	lastContentId = content.id

	#print the article id and time every 1000 articles
	if int(content.id)%1000 == 0:
		global start
		print content.id, time.strftime('%H:%M:%S', time.gmtime(time.time() - start))

	#Find all of the links. If the page is in the links, print it
	links = linksPattern.findall(content.text)
	for page in pages:
		if page['title'] in links:
			page['referenceCount']+=1

if __name__ == "__main__":
	with codecs.open('out.txt',encoding='utf-8') as pagesFile:
		pages = json.load(pagesFile)
		print 'Done loading json'
		print 'loaded %d pages'%len(pages)

	for page in pages:
		page['referenceCount'] = 0

	try:
		start = time.time()
		page_parser.parseWithCallback(sys.argv[1], contentHandler)
	except KeyboardInterrupt:
		pass
	finally:
		with codecs.open('eventswithreferences.json','w', encoding='utf-8') as outFile:
			try:
				for page in pages:
					print page['title'],page['referenceCount']
				outFile.write(json.dumps(pages))
				print "left off at: ",lastContentId
			except:
				pdb.set_trace()