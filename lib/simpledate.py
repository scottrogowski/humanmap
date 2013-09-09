import re
import pdb
import math
bcPattern = re.compile(r'(\s|\d)b\.?\s?c\.?\s?e?',re.IGNORECASE)

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
	"spring" : 3, "summer" : 6, "fall" : 9
	}

class SimpleDate:
	'''
	SimpleDate is needed because python dates do not support BC
	'''
	year = 0
	month = 0
	day = 0

	def __init__(self,year,month,day):
		self.year = int(year)
		self.month = int(month)
		self.day = int(day)

	def __str__(self):
		return str(self.month)+'/'+str(self.day)+'/'+str(self.year)

	def toDict(self):
		#for json parsing
		return {
			'year':self.year,
			'month':self.month,
			'day':self.day
			}

	def completeness(self):
		'''
		A measure of how good this date is
		'''
		ret = 0
		if self.year!=0:
			ret += 4
		if self.month!=0:
			ret += 2
		if self.day!=0:
			ret += 1
		return ret

def isInt(s):
	try:
		if not math.isnan(int(s)):
			return True
		raise
	except:
		return False


def parse(preparedString,endDate=False):
	'''
	Parse the string into a SimpleDate (year, month, day supporting negative years)

	The rules are complex but seem to work great for wikipedia dates at least
	'''
	year = month = day = 0

	if '{{' in preparedString and '}}' in preparedString:
		if len(preparedString.split('|'))==4:
			#For very well formatted wikipedia dates
			preparedString = preparedString[preparedString.find('{')+2:preparedString.rfind('}')-1]
			splitString = preparedString.split('|')
			year = splitString[1]
			month = splitString[2]
			day = splitString[3]
			return SimpleDate(year,month,day)
		else:
			#for wikipedia dates that tried to be well formatted but failed miserably
			preparedString = preparedString.replace('{','').replace('}','').replace('|',' ')

	#if it is BC, we should be able to spot that immediately
	if bcPattern.search(preparedString):
		BCE = True
	elif endDate and endDate.year<0:
		BCE = True
	else:
		BCE = False

	#remove commas
	preparedString = preparedString.replace(',','').replace('\n','')

	#split the string into tokens
	splitString = re.split('\s|\/|(?:&nbsp;)',preparedString)
	splitString = map(lambda x: x.lower(),splitString)

	#If length is 0, the number is the year. Return that
	#if len(splitString)==1:
	#	year = splitString[0]

	#search for named months first
	for m in MONTHS:
		if m in splitString:
			month = MONTHS[m]
			wasStringMonth = True
			break
	else:
		wasStringMonth = False

	numericDates = map(lambda x: int(x), filter(lambda x: isInt(x), splitString))

	#Days must be less than 31
	possibleDays = filter(lambda x: int(x)<=31, numericDates)
	if len(possibleDays):
		day = possibleDays[0]
		numericDates.remove(day)

	#all of the integer tokens. These might be date part
	#Years are more likely than not to be greater than 31
	likelyYears = filter(lambda x: int(x)>31, numericDates)
	if len(likelyYears):
		year = likelyYears[0]
		numericDates.remove(year)
		if BCE:
			year*=-1
	elif endDate:
		year = endDate.year

	#If we have not yet gotten a month, try the enddate month
	#possibleMonths = filter(lambda x: int(x)<=12,numericDates)
	if not month and endDate and endDate.month:
		month = endDate.month

	#if we have not yet gotten a year, it might be <31AD or >31BC. Try this
	if not year and numericDates:
		year = numericDates[0]
	elif not year and day:
		#If we had pulled a day but had no year, this is actually the year
		year = day
		day = 0

	#If we couldn't get the year, the date failed
	if not year:
		return False

	return SimpleDate(year,month,day)

def parseDate(raw):
	'''
	take a raw date and return the start and end dates
	'''
	print raw#tounicode
	raw = raw.decode('utf-8')
	raw = raw.replace(u'\xe2','-').replace(u'\u2013','-')
	if '-' in raw:
		print '- in raw'
		startEnd = raw.split('-')
		end = parse(startEnd[1])
		start = parse(startEnd[0],end)
	else:
		start = end = parse(raw)

	print str(start) + ' - ' + str(end)
	print
	print
	return start,end


if __name__ == "__main__":
	#testing function
	with open('seed.txt') as f:
		for line in f:
			if line:
				parseDate(line)