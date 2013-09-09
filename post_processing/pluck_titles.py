import codecs
import json 

if __name__ == "__main__":
	'''Find all titles in the file and write them'''
	with codecs.open('out.txt',encoding='utf-8') as inFile:
		pagesLoaded = json.load(inFile)
		titlesToReprocess = map(lambda x: x['title'], pagesLoaded)

	with codecs.open('titlesToReprocess.json','w', encoding='utf-8') as outFile:
		outFile.write(json.dumps(titlesToReprocess))
	print "Done writing titles"