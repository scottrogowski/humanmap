"""
When run as a script, takes one argument indicating the location of an XML
dump from a media wiki, and parses the entire file, searching for <page>
elements.

Each <page> is turned into a WikiPage object. A callback can be defined to
receive the page.

Read more about dumps here: http://meta.wikimedia.org/wiki/Data_dumps
"""

import sys
import pdb
from xml.sax import handler, make_parser #xml.sax is not custom code
from xml.sax.saxutils import XMLFilterBase
from xml.sax.xmlreader import Locator

class WikiPage(object):
	"""
	Holds data related to one <page> element parsed from the dump
	"""
	def __init__(self):
		self.title = u''
		self.id = u''
		self.text = u''
		self.infoBoxType = u''
		self.rawDate = u''
		self.dateType = u''
		self.coordinates = u''
		self.categories = u''
		self.firstParagraph = u''
		self.img = u''

	'''
	def postToDB(self):

		devent = Devent(
			title = self.title,
			,wikipediaID = self.id
			,text = self.text
			,infoBoxType = self.infoBoxType
			,rawDate = self.rawDate
			,
			id,text,infoBoxType,)
		venue = Venue(
			coordinates = self.TODO
			)
	'''


	def __unicode__(self):
		instanceStr =  self.title +'\n'
		instanceStr += self.id + '\n'
		instanceStr += str(self.coordinates) +'\n'
		instanceStr += str(self.startDate) + ' - ' + str(self.endDate) +'\n'
		#instanceStr += self.img +'\n'
		#instanceStr += self.firstParagraph +'\n'
		#for category in self.categories:
		#   instanceStr += ' - '+category +'\n'
		instanceStr += '\n\n'
		return instanceStr

	def __repr__(self):
		return self.id

	def toDict(self):
		return {
			'title':self.title,
			'id':self.id,
			'coordinates':self.coordinates.toDict(),
			'startDate':self.startDate.toDict(),
			'endDate':self.endDate.toDict(),
			'img':unicode(self.img),
			'firstParagraph':unicode(self.firstParagraph),
			'categories':unicode(self.categories),
			}



class TextNormalizeFilter(XMLFilterBase):
	"""
	SAX filter to ensure that contiguous texts nodes are merged into one
	That hopefully speeds up the parsing process a lot, specially when reading
	revisions with long text
	Receip by Uche Ogbuji, James Kew and Peter Cogolo
	Retrieved from "Python Cookbook, 2nd ed., by Alex Martelli, Anna Martelli
	Ravenscroft, and David Ascher (O'Reillly Media, 2005) 0-596-00797-3"
	"""
	def __init__(self, upstream, downstream):
		XMLFilterBase.__init__(self, upstream)
		self._downstream=downstream
		self._accumulator=[]
	def _complete_text_node(self):
		if self._accumulator:
			self._downstream.characters(''.join(self._accumulator))
			self._accumulator=[]
	def characters(self, text):
		self._accumulator.append(text)
	def ignorableWhiteSpace(self, ws):
		self._accumulator.append(text)
def _wrap_complete(method_name):
	def method(self, *a, **k):
		self._complete_text_node()
		getattr(self._downstream, method_name)(*a, **k)
	method.__name__= method_name
	setattr(TextNormalizeFilter, method_name, method)
for n in '''startElement endElement endDocument'''.split():
	_wrap_complete(n)

documentLocator = Locator()

class WikiDumpHandler(handler.ContentHandler):
	"""
	This extends handler ContentHandler

	A ContentHandler designed to pull out page ids, titles and text from
	Wiki pages. These are assembled into WikiPage objects and sent off
	to the supplied callback.


	"""
	def __init__(self, pageCallBack=None):
		handler.ContentHandler.__init__(self)
		self.currentTag = ''
		self.ignoreIdTags = False
		self.pageCallBack = pageCallBack
		self.pagesProcessed = 0
		#self.setDocumentLocator(documentLocator)

	'''
	def setDocumentLocator(self,locator):
		self.locator = locator
		return
	'''

	def startElement(self, name, attrs):
		self.currentTag = name
		if (name == 'page'):
			# add a page
			self.currentPage = WikiPage()

		elif (name == 'revision'):
			# when we're in revision, ignore ids
			self.ignoreIdTags = True

	def endElement(self, name):
		if (name == 'page'):
			if self.pageCallBack is not None:
				self.pageCallBack(self.currentPage)
			self.pagesProcessed += 1
			#if not self.pagesProcessed%10:
		elif (name == 'revision'):
			# we've finished the revision section
			self.ignoreIdTags = False
		self.currentTag = ''

	def characters(self, content):
		if self.currentTag == 'id' and not self.ignoreIdTags:
			self.currentPage.id = content
		elif self.currentTag == 'title':
			self.currentPage.title = content
		elif self.currentTag == 'text':
			self.currentPage.text = content

	def endDocument(self):
		#self.pb.finish()
		print "Processed %d pages" % self.pagesProcessed

def parseWithCallback(inputFileName, callback):
	parser = make_parser() #xml.sax

	#Set the featurename to value. If the feature is not recognized, SAXNotRecognizedException is raised. If the feature or its setting is not supported by the parser, SAXNotSupportedException is raised.
	parser.setFeature(handler.feature_namespaces, False) #Do not perform namespace processing

	# apply the TextNormalizeFilter
	wdh = WikiDumpHandler(pageCallBack=callback)
	filter_handler = TextNormalizeFilter(parser, wdh)

	filter_handler.parse(open(inputFileName))

def printPage(page):
	#default print page like ID 3768 TITLE Bundestag
	#not sure how it knows about the title but it might not matter
	print page

if __name__ == "__main__":
	"""
	When called as script, argv[1] is assumed to be a filename and we
	simply print pages found.
	"""
	parseWithCallback(sys.argv[1], printPage)