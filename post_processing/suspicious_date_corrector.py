'''
This will loop through the json looking for dates which might be incorrect and will allow you to correct them one-by-one
'''
import json
import codecs
import sys
import pprint

filename = sys.argv[1]
with codecs.open(filename,encoding='utf-8') as inFile:
	pagesLoaded = json.load(inFile)

#possiblyOff = filter(lambda page: page['startDate']['year']>=0 and page['startDate']['year']<=31,pagesLoaded)

try:
	for i, page in enumerate(pagesLoaded):
		if page['startDate']['year']>=0 and page['startDate']['year']<=31:
			print page['title']
			print page['firstParagraph']
			print page['preparedDate']
			print "start:",page['startDate']
			print "end:",page['endDate']
			
			if raw_input("Correct?") != 'y':
				page['startDate']['year'] = page['endDate']['year'] = raw_input("Year?")
				page['startDate']['month'] = page['endDate']['month'] = raw_input("Month?")
				page['startDate']['day'] = page['endDate']['day'] = raw_input("Day?")
				pagesLoaded[i] = page
except KeyboardInterrupt:
	pass
finally:
	with codecs.open(filename,'w',encoding='utf-8') as outFile:
		outFile.write(json.dumps(pagesLoaded))

	
