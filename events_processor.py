#/usr/bin/python
import sys
import pdb
import re
from pprint import pprint
import argparse
import operator
#import progressbar
import codecs
import json

import lib.page_parser as page_parser
#import lib.article_processor as article_processor
from lib.extractBetween import extractBetween
import lib.coordinate_parser as coordinate_parser
from lib.wikipedia_exceptions import *
import lib.simpledate as simpledate

DEBUG = True

#loaded in via JSON in case of an interrupt
pagesLoaded = []
lastPageParsed = 0
import dateutil.parser as parser
import datetime
import re



coorsPattern = re.compile(r"\s*\{\{[Cc]oord\|(.*?)\}\}\s*",re.MULTILINE) #Will have this before closing </page> tag if available
categoryPattern = re.compile(r"^\s*\[\[[Cc]ategory\:(.*?)\|?\s*\]\]\s*",re.MULTILINE)
firstParagraphPattern = re.compile(r"^\s*\n(\'\'\')?\w",re.MULTILINE)
infoBoxPattern = re.compile(r"\{\{Infobox\s+.*\}\}",re.DOTALL) #dotall allows newline to match
refsPattern = re.compile(r"(?:<ref\s.*?\/>)|(?:<ref.*>.*?<\/ref>)",re.DOTALL)
commentPattern = re.compile(r"<\!\-\-.*?\-\->",re.DOTALL)
boldPattern = re.compile(r"\'\'\'(.*?)\'\'\'")
complexLinkPattern = re.compile(r"\[\[(.*?)\|(.*?)\]\]") #two part link
linkPattern = re.compile(r"\[\[(.*?)\]\]") #one part link

bracketPattern = re.compile(r"\{\{.*?\}\}")
squareBracketPattern = re.compile(r"\[.*?\]")
parenthesisPattern = re.compile(r"\(.*?\)")
imgPattern = re.compile(r"\[\[(?:File|Image)\:(.*?)\|(?:thumb|\d+px).*\]\]")
bcPattern = re.compile(r'(\s|\d)b\.?\s?c\.?\s?e?',re.IGNORECASE)
slashPattern = re.compile(r'(^|\s)([a-z]+?)\s?\/\s?([a-z]+?)\s',re.IGNORECASE) # for battle of marathon august/september 490 bc
centuryPattern = re.compile(r'(\d*(1st|2nd|3rd|[4-90]th))\s+century',re.IGNORECASE)
ymdPattern = re.compile(r'(\d{1,4})\|(\d{1,2})\|(\d{1,2})')
brPattern = re.compile(r'<br\s?\/?>')

'''
typeCounts = {}
dateCounts = {}
categoryCounts  = {}
'''



#Most important structure of this file
pages = []


'''
Example from battle of bosworth field
==External links==
{{Commons category|Battle of Bosworth Field}}
* [http://www.bosworthbattlefield.com Bosworth Battlefield Heritage Centre and Country Park]: website for the museum, contains information and photos about current state of the battlefield
* [http://www.r3.org/bosworth/ Richard III Society]: history society, which contains photos and articles that present several competing theories about the location of the battle

{{Wars of the Roses}}

{{coord|52|35|28|N|1|24|37|W|type:event_region:GB_source:enwiki|display=title}}

{{featured article}}
#occassionally, there will be other coordinates in the article but they should be like Ambion Hill (523441N 12602W)) #this does not get rendered
'''




"""
def processPage(page):
	'''
	Check through the page for coordinates and that it is a military conflict with a date.
	If this is all true, parse the page and append it to the "pages" array
	'''

	if titlesToReprocess and page.title not in titlesToReprocess:
		return False

	#pages are loaded from where we last left off in case of an interrupt
	#lastPageParsed is the id of the last page in the json file
	#continue through the xml until we find a page that has not been parsed
	if int(page.id) < int(lastPageParsed):
		return False

	#If no coordinates, return False
	cp = coorsPattern.search(page.text)
	if not cp:
		return False

	#If there is no infobox (where the date would be) return false
	ibStart = page.text.find('{{Infobox')
	if ibStart == -1:
		return False

	#Get the infobox
	ib = extractBetween(page.text,"{{","}}",ibStart)
	ibarray = ib.splitlines()

	#If the infobox is less than two lines, there is likely no content so return false
	if len(ibarray)<2:
		return False

	#TODO default indentation and kill those lines without it
	#ibarray = re.split(r'\n\s*\|',ib)

	#get info box type (e.g. military conflicts)
	page.infoBoxType = ibarray[0]
	page.infoBoxType = page.infoBoxType[page.infoBoxType.find(' '):].strip()

	#for now, we are only covering military battles
	if page.infoBoxType != 'military conflict':
		return False

	#reduce the infobox array to be only everything after the infoboxtype
	ibarray = ibarray[1:]
	ibarray = filter(lambda x: '|' in x, ibarray)

	#Reduce the infobox array to be sure we are not in subinfoboxes
	indentationLevel = ibarray[0].find('|')
	ibarray = filter(lambda x: len(x)>indentationLevel and x[indentationLevel]=='|',ibarray)
	ibarray = map(lambda x: x[indentationLevel+1:],ibarray)

	#Map the infobox into key=values.
	#Be sure each key has an associated value
	#Be sure each value has a length
	ibkeyval = map(lambda x: map(lambda y: y.strip(), x.split('=',1)), ibarray)
	ibkeyval = filter(lambda x: len(x)==2,ibkeyval)
	ibkeyval = filter(lambda x: x[1].strip(),ibkeyval)

	#Change the keyvals into a dict
	ibdict = dict(ibkeyval)

	#Check if any of our possible date identifiers are in the infobox
	#if any matches, use that for a rawDate and record which date identifier we used
	for key in DATEKEYS:
		try:
			page.rawDate = ibdict[key]
			page.dateType = key
			break
		except KeyError:
			continue
	else:
		#May 13th incident in Malysia breaks this because it has no date in infobox
		return False

	#apply some transformations to the date string to make it parsable
	preparedDates = cls._processRawDate(page.rawDate)
	preparedDates = map(lambda x: PreparedDate(x),preparedDates)

	try:
		maxCompleteness = -1
		for preparedDate in preparedDates:
			preparedDate.calculate()
			if preparedDate.completeness()>maxCompleteness:
				page.preparedDate = preparedDate.date
				page.startDate = preparedDate.startDate
				page.endDate = preparedDate.endDate
	except Exception, e:
		#We have been free from this in 700 events so far
		print e
		pdb.set_trace()

	#If the parser can't find a year, it will return false.
	#If this happens, forget about this event
	if not page.endDate or not page.startDate:
		return False

	#Handle coordinates
	try:
		page.coordinates = Coords(cp.group(1))
		''' TODO in infobox
			| lat_degrees     = 38
			| lat_minutes     = 53
			| lat_seconds     = 21.48
			| lat_direction   = N
			| long_degrees    = 77
			| long_minutes    = 3
			| long_seconds    = 0.40
			| long_direction  = W
		'''
	except:
		#battle of san pasqual is the first to break this.
		#We could probably parse these coordinates like this....
		#TODO
		#33|5|10|N|116|59|24|W|region:US-CA_type:event_source:GNIS|display=title|notes=<ref>{{Cite gnis|248945|San Pasqual Battlefield State Historic Park}}</ref>
		return False

	#Categorize this event
	try:
		page.categories = categoryPattern.findall(page.text)
		page.categories.append(page.infoBoxType)
		try:
			if page.categories[0][-2:] == '|*':
				#Remove this which pops up when the article title is the category
				page.categories[0] = page.categories[0][:-2]
		except:
			pass
		#page.categories = map(lambda x: page.dateType + ' of ' + pluralize(x), page.categories )
	except:
		pdb.set_trace()

	#Get the first paragraph of this event
	try:
		start = firstParagraphPattern.search(page.text).start()
		page.firstParagraph = page.text[start:]
		end = page.firstParagraph.find('==')
		if end!=-1:
			page.firstParagraph = page.firstParagraph[:end]
		#raw_input()
		page.firstParagraph = normalizeLinksAndFormatting(page.firstParagraph)
	except:
		#This first fails on battle of noda castle
		return False

	#Get the image
	try:
		page.img = imgPattern.search(page.text).group(1)
	except:
		#this fails whenever there is no image in the article and this is fine
		page.img = ''

	#Print the page as it is
	if DEBUG:
		print unicode(page)

	#Append it and list the number of pages parsed so far
	pages.append(page)
	print len(pages)+len(pagesLoaded)

	'''
	try:
		typeCounts[page.infoBoxType] += 1
	except:
		typeCounts[page.infoBoxType] = 1
	try:
		dateCounts[key] += 1
	except:
		dateCounts[key] = 1

	for category in page.categories:
		try:
			categoryCounts[category] += 1
		except:
			categoryCounts[category] = 1

	'''
	return True
"""


bigExceptions = 0

class ArticleProcessor(object):
	ACCEPTABLE_INFOBOX_TYPE = 'military conflict'

	DATEKEYS = ('year','date','foundation','formation','formed','established','introduced','first_flight'
		,'completion_date','established_date','established_date1','launch_date','year_start','year_end'
		,'AdmittanceDate','launch','liberated by','inauguration_date','start_date','start','end','|date') #'death_date','birth_date'

	MONTHS = {
			"january" : 1, "jan" : 1,
			"february" : 2, "feb" : 2,
			"march" : 3, "mar" : 3,
			"april" : 4, "apr" : 4,
			"may" : 5, "May" : 5,
			"june" : 6, "jun" : 6,
			"july" : 7, "jul" : 7,
			"august" : 8, "aug" : 8,
			"september" : 9, "sep" : 9, "sept": 9,
			"october" : 10, "oct" : 10,
			"november" : 11, "nov" : 11,
			"december" : 12, "dec" : 12,
		}

	DATESEPERATERS = [' to ','&ndash;',u'\xe2',u'\u2013']


	def __init__(self,page):
		self.page = page

	def process(self):
		cls = self.__class__
		try:
			#basic check
			cls.checkShouldProcess(self.page.title,self.page.id)

			#No need for refs anywhere
			
			self.page.text = cls._removeRefs(self.page.text)

			#Info box
			self.page.infoBoxType, self.page.infoBoxDict = InfoBox.process(text=self.page.text,acceptableInfoBoxType=cls.ACCEPTABLE_INFOBOX_TYPE)

			#Set page variables
			self.page.coordinates = cls.getCoordinates(text=self.page.text, infoBoxDict=self.page.infoBoxDict)
			self.page.firstParagraph = cls.getFirstParagraph(text=self.page.text)
			self.page.img = cls.getImage(text=self.page.text)
			
			self.page.startDate, self.page.endDate = cls.getDate(infoBoxDict=self.page.infoBoxDict)
			
			#Print the page as it is
			if DEBUG:
				print unicode(self.page)
				global bigExceptions
				print "Number of big exceptions: "+str(bigExceptions)

			return self.page
		except ContinueException:
			return False
		except MinorException,e:
			print "\"%s\": Could not process because \"%s\""%(self.page.title,e)
			return False
		except PageProcessorException,e:
			if DEBUG:
				print "Could not process %s because \"%s\""%(self.page.title,e)
				pdb.set_trace()
			global bigExceptions
			bigExceptions += 1
			return False

	@classmethod
	def checkShouldProcess(cls,title,page_id):
		'''
		Step 1
		'''
		if titlesToReprocess and title not in titlesToReprocess:
			raise MinorException("Not a title that should be processed")

		#pages are loaded from where we last left off in case of an interrupt
		#lastPageParsed is the id of the last page in the json file
		#continue through the xml until we find a page that has not been parsed
		if int(page_id) < int(lastPageParsed):
			raise MinorException("Already processed this title")


	@classmethod
	def getCoordinates(cls,text,infoBoxDict):
		'''
		Step 5
		'''
		#{{coord|55.72746|-3.02057|type:landmark_region:GB_source:enwiki-osgb36(NT360487)|display=title}}
		cp = coorsPattern.search(text)

		if cp:
			return coordinate_parser.InlineCoords(cp.group(1))
		else:
			if 'lat_d' in infoBoxDict and 'long_d' in infoBoxDict:
				#print "Trying infobox coords"
				return coordinate_parser.InfoBoxCoords(lat=infoBoxDict['lat_d'],lng=infoBoxDict['long_d'])
			else:
				raise MinorException("Could not find valid coordinates!")


	@classmethod
	def getFirstParagraph(cls,text):
		'''
		Step 9
		Get the first paragraph of this event
		'''
		try:
			start = firstParagraphPattern.search(text).start()
			firstParagraph = text[start:]
			end = firstParagraph.find('==')
			if end!=-1:
				firstParagraph = firstParagraph[:end]
			return cls._normalizeLinksAndFormatting(firstParagraph)
		except Exception, e:
			#No big deal if we can't find the first paragraph
			return ''
			#print e
			#raise PageProcessorException("Could not get the first paragraph")

	@classmethod
	def getImage(cls,text):
		'''
		Step 10
		'''
		#Get the image
		try:
			return imgPattern.search(text).group(1)
		except:
			#this fails whenever there is no image in the article and this is fine
			return ''

	@classmethod
	def getDate(cls,infoBoxDict):
		#Check if any of our possible date identifiers are in the infobox
		#if any matches, use that for a rawDate and record which date identifier we used
		for key in cls.DATEKEYS:
			try:
				rawDate = infoBoxDict[key]
				dateType = key
				break
			except KeyError:
				continue
		else:
			#May 13th incident in Malysia breaks this because it has no date in infobox
			raise MinorException("No date in infobox")

		#apply some transformations to the date string to make it parsable
		preparedDates = cls._processRawDate(rawDate)
		preparedDates = map(lambda x: PreparedDate(x),preparedDates)

		try:
			maxCompleteness = -1
			for preparedDate in preparedDates:
				preparedDate.calculate()
				if preparedDate.completeness()>maxCompleteness:
					#print 'preparedDate',preparedDate,preparedDate.startDate,preparedDate.endDate
					#preparedDate = preparedDate.date
					startDate = preparedDate.startDate
					endDate = preparedDate.endDate
		except Exception, e:
			#We have been free from this in 700 events so far
			print e
			pdb.set_trace()

		#If the parser can't find a year, it will return false.
		#If this happens, forget about this event
		if not endDate or not startDate:
			raise MinorException("Could not parse date")

		return startDate, endDate

	@classmethod
	def getCategories(cls,text,infoboxtype):
		#Categorize this event
		try:
			categories = categoryPattern.findall(text)
			categories.append(infoBoxType)
			try:
				if categories[0][-2:] == '|*':
					#Remove this which pops up when the article title is the category
					categories[0] = categories[0][:-2]
			except:
				pass
			#page.categories = map(lambda x: page.dateType + ' of ' + pluralize(x), page.categories )
			return categories
		except:
			pdb.set_trace()


	'''
	HELPER FUNCTIONS
	'''

	@classmethod
	def _removeRefs(cls,text):
		'''
		Remove wikipedia refs
		'''
		text = refsPattern.sub('',text)
		text = commentPattern.sub('',text)
		return text

	@classmethod
	def _normalizeLinksAndFormatting(cls,text):
		'''
		Change wikipedia formatting to HTML formatting
		'''
		#text = cls._removeRefs(text)
		text = bracketPattern.sub('',text)
		while True:
			start = text.find('[[')
			end = text.find(']]')
			if start==-1 or end==-1 or start>end:
				break
			link = text[start+2:end]

			if '|' in link:
				vals = link.split('|')
				link = vals[0]
				linkName = vals[1]
			else:
				linkName = link
			link = link.replace(' ','_')

			text = text[:start] + "<a href='http://en.wikipedia.org/wiki/%s'>%s</a>"%(link,linkName) + text[end+2:]

		text = text.replace('\n','<br>')
		text = boldPattern.sub("<b>\g<1></b>",text)
		return text

	@classmethod
	def _processRawDate(cls,rawDate):
		'''
		Remove references
		remove all lines except first line
		remove links
		remove shit inside of parenthesis and brackets
		if it is like '10th century', convert that to 900
		'''
		text = cls._removeRefs(rawDate)
		#text = text.split('<br')[0]
		text = unicode(text)
		#try:
		#	text = text.decode('utf-8')

		#Remove links
		clp = complexLinkPattern.search(text)
		if clp:
			text = complexLinkPattern.sub(r'\2',text)
		lp = linkPattern.search(text)
		if lp:
			text = linkPattern.sub(r'\1',text)

		#Remove parenthesis and brackets
		text = parenthesisPattern.sub('',text)
		text = squareBracketPattern.sub('',text)

		#Convert 10th century to 900
		cp = centuryPattern.match(text)
		if cp:
			century = int(re.sub(r'\D','',cp.group(1))) #remove nondigits
			century = (century-1)*100
			text = text.replace(cp.group(0),str(century))
		
		#Replace all date seperaters with '-'
		for delim in cls.DATESEPERATERS:
			if delim in text:
				text = text.replace(delim,'-')

		#If start-date or end-date are in there, replace those with start, end and clean up the brackets
		if 'tart-date' in text and 'nd-date' in text and '{{' in text and '}}' in text:
			text = text.replace('-date','')
			text = re.sub(r'\}\}\s*\{\{','}}-{{',text)

		#Sometimes a page break is included and sometimes the good date is on top and sometimes on the bottom
		return brPattern.split(text)


class PreparedDate(object):
	def __init__(self,date):
		self.date = date

	def calculate(self):
		if '-' in self.date:
			#If this is a date range, parse the start and enddates seperately
			#The parser uses information from the endDate to fill in some info about the start date
			#And sometimes, the startdate has a month and the end does not so we fill that back in
			startEnd = self.date.split('-')
			self.endDate = simpledate.parse(startEnd[1])
			self.startDate = simpledate.parse(startEnd[0],self.endDate)
			if self.startDate and self.endDate and self.startDate.month and not self.endDate.month:
				self.endDate.month = self.startDate.month
		else:
			self.startDate = self.endDate = simpledate.parse(self.date)		

	def completeness(self):
		completeness = 0
		if self.startDate:
			completeness += self.startDate.completeness()
		if self.endDate:
			completeness += self.endDate.completeness()
		return completeness


class InfoBox(object):
	@classmethod
	def process(cls,text,acceptableInfoBoxType):
		infoBoxArray = cls.getInfoBoxArray(text=text)
		infoBoxType = cls.getInfoBoxType(infoBoxArray=infoBoxArray,acceptableInfoBoxType=acceptableInfoBoxType)			
		infoBoxDict = cls.getInfoBoxDict(infoBoxArray=infoBoxArray)
		return (infoBoxType,infoBoxDict)

	@classmethod
	def getInfoBoxArray(cls,text):
		'''
		Step 2
		'''
		ibStart = text.find('{{Infobox')
		if ibStart == -1:
			raise ContinueException("Could not find infobox")

		#Get the infobox
		ibString = extractBetween(text,"{{","}}",ibStart)

		'''
		infoBoxArray = []
		ibCounter = 0
		accumulatedString = ''
		for char in ibString:
			if char in ('[','{'):
				ibCounter+=1
			elif char in (']','}'):
				ibCounter-=1
			elif char == '|' and ibCounter==0:
				infoBoxArray.append(accumulatedString)
				accumulatedString=''
			accumulatedString+=char
		infoBoxArray.append(accumulatedString)
		'''
		infoBoxArray = ibString.splitlines()

		#pprint(infoBoxArray)

		if len(infoBoxArray)<2:
			raise ContinueException("Infobox array less than 2 long")

		#infoBoxArray = map(lambda arr: '|'+arr,infoBoxArray)
		return infoBoxArray

	@classmethod
	def getInfoBoxType(cls,acceptableInfoBoxType,infoBoxArray):
		'''
		Step 3
		'''
		#TODO default indentation and kill those lines without it
		#infoBoxArray = re.split(r'\n\s*\|',ib)

		#get info box type (e.g. military conflicts)
		infoBoxType = infoBoxArray[0]
		infoBoxType = infoBoxType[infoBoxType.find(' '):].strip()

		if infoBoxType != acceptableInfoBoxType:
			raise ContinueException("Infoboxtype was not of type '%s'",acceptableInfoBoxType)
			
		return infoBoxType


	@classmethod
	def getInfoBoxDict(cls,infoBoxArray):
		'''
		Step 4
		'''

		#reduce the infobox array to be only everything after the infoboxtype
		infoBoxArray = infoBoxArray[1:]
		infoBoxArray = filter(lambda x: '|' in x, infoBoxArray)

		#Reduce the infobox array to be sure we are not in subinfoboxes
		indentationLevel = infoBoxArray[0].find('|')
		infoBoxArray = filter(lambda x: len(x)>indentationLevel and x[indentationLevel]=='|',infoBoxArray)
		infoBoxArray = map(lambda x: x[indentationLevel+1:],infoBoxArray)

		#Map the infobox into key=values.
		#Be sure each key has an associated value
		#Be sure each value has a length
		ibkeyval = map(lambda x: map(lambda y: y.strip(), x.split('=',1)), infoBoxArray)
		ibkeyval = filter(lambda x: len(x)==2,ibkeyval)
		ibkeyval = filter(lambda x: x[1].strip(),ibkeyval)

		if not ibkeyval:
			raise PageProcessorException("No key values in dict")

		#Change the keyvals into a dict
		return dict(ibkeyval)


def processPage(page):
	"""
	If the page parses without errors (most will not), append it to the "pages" array
	"""
	#Generate the page
	pageProcessor = ArticleProcessor(page)
	page = pageProcessor.process()
	if not page:
		return False

	#Append it and list the number of pages parsed so far
	pages.append(page)
	print len(pages)+len(pagesLoaded)
	return True

titlesToReprocess = []

if __name__ == "__main__":
	'''
	This script will open the xml wikipedia dump (probably called enwiki-latest-pages-articles.xml)
	and will find articles with coordinates and dates.
	If these articles are also about military conflicts (this much is easily changed), add these files
	to the internal pages array. Save these articles as a json.
	'''

	cli = argparse.ArgumentParser(description="Pull military conflicts with dates and coordinates out of wikipedia and put them in a JSON")
	cli.add_argument('inXML', help='The big ass wikipedia dump') #
	cli.add_argument('outJSON',help='Where to put your rendered json',default='out.json')
	cli.add_argument('-t', dest='titlesJSON',help='A list of titles to go over again to speed things up a bit',default=None)
	cli.add_argument('-n', dest='startNew',help="Start over fresh (overwrites json file)")
	args = cli.parse_args()


	#Get the already parsed pages which are stored in a json file
	if not args.startNew:
		try:
			with codecs.open(args.outJSON,encoding='utf-8') as outJSON:
				pagesLoaded = json.load(outJSON)
				print 'done loading json'
				lastPageParsed = pagesLoaded[-1]['id']
		except:
			pass

	if args.titlesJSON:
		with codecs.open(args.titlesJSON, encoding='utf-8') as titlesJSON:
			titlesToReprocess = json.load(titlesJSON)
		
	#Open the xml file and start parsing
	try:
		page_parser.parseWithCallback(args.inXML, processPage)
	except KeyboardInterrupt:
	   pass
	except Exception, e:
		print e
		pdb.set_trace()
	finally:
		#Write the parsed pages to the out.txt file if we have at least parsed one new page
		#(this requirement is to be sure we don't overwrite with an incomplete pagesLoaded)
		if pages:
			with codecs.open(args.outJSON,'w', encoding='utf-8') as outFile:
				try:
					pages = map(lambda x:x.toDict(),pages)
					outFile.write(json.dumps(pagesLoaded+pages))
				except:
					pdb.set_trace()

		print
		print "Done parsing: ", args.inXML
		print str(len(pagesLoaded)+len(pages))+' pages found'

		'''
		print "type counts"
		print len(typeCounts)
		sorted_x = sorted(typeCounts.iteritems(), key=operator.itemgetter(1))
		pprint(sorted_x[-10:])

		print "date counts"
		print len(dateCounts)
		sorted_x = sorted(dateCounts.iteritems(), key=operator.itemgetter(1))
		pprint(sorted_x[-10:])

		print "category counts"
		print len(categoryCounts)
		sorted_x = sorted(categoryCounts.iteritems(), key=operator.itemgetter(1))
		pprint(sorted_x[-10:])
		'''


