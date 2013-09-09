import re
from wikipedia_exceptions import *

class Coords(object):
	"""
	class to parse and hold coord data
	"""
	def toDict(self):
		return {
			'lat':self.lat,
			'lng':self.lng
			}

	def __str__(self):
		return "%f|%f" % (self.lat, self.lng)
	def __unicode__(self):
		return "%f|%f" % (self.lat, self.lng)


class InlineCoords(Coords):
	'''
	Like {{coord:}}
	'''
	delim = re.compile(r"\s*\|\s*")
	valid = re.compile(r"^[0-9\.\-+NSEW]+$")
	granularities = [1, 0.0166666, 0.000166666]
	points = {"N": 1, "S": -1, "E": 1, "W": -1}

	def __init__(self, coordStr):
		coordStr = coordStr.strip()
		#print coordStr
		#pdb.set_trace()
		pieces = [x for x in self.delim.split(coordStr) if self.valid.match(x)] #split across '|' and strip
		if not pieces:
			raise ValueError()

		numPieces = len(pieces)

		#If we have an odd number of pieces, 
		if numPieces % 2 != 0:
			pieces = self._padPieces(pieces, numPieces)
			numPieces = len(pieces)

		gran, self.lat = 0, 0
		for piece in pieces[:(numPieces / 2)]:
			self.lat = self._process(self.lat, piece, gran)
			gran += 1

		gran, self.lng = 0, 0
		for i, piece in enumerate(pieces[(numPieces/2):]):
			self.lng = self._process(self.lng, piece, i)

	def _process(self, dimension, piece, gran):
		if self.points.has_key(piece):
			return dimension * self.points[piece]
		elif gran > 2:
			raise ValueError()
		else:
			return dimension + (float(piece) * self.granularities[gran])

	def _padPieces(self, pieces, numPieces):
		divider = 0
		for piece in pieces:
			#IF N, S, E, W are not in piece, increment the divider
			if not self.points.has_key(piece):
				divider += 1
			else:
				break
		#If there were no N,S,E,W in coords, value error
		if divider == numPieces:
			raise ValueError()
		latPieces = pieces[:divider + 1]
		longPieces = pieces[divider + 1:]
		while len(latPieces) < 4:
			latPieces.insert(-1, "0")
		while len(longPieces) < 4:
			longPieces.insert(-1, "0")
		latPieces.extend(longPieces)
		return latPieces

class InfoBoxCoords(Coords):
	'''
	Coordinates found in the infobox which look like
	| lat_d =   6 | lat_m =  5 | lat_s = | lat_NS = :
	| long_d= 116 | long_m= 33 | long_s= | long_EW= E
	OR
	| lat_d = 41.409196033
	| long_d = -122.194888358

	'''

	def __init__(self,lat,lng):
		print lat,lng
		try:
			'''
			Try to see whether it is simple first like 41.409196033
			'''
			self.lat = float(lat)
			self.lng = float(lng)
		except ValueError:
			lat=str(lat)
			lng=str(lng)
			if '|' in lat and '|' in lng:
				self.lat = self._processComplex(lat)
				self.lng = self._processComplex(lng)
			else:
				raise PageProcessorException("Could not get infobox coords %s, %s",lat,lng)


	def _processComplex(self,dimension):
		'''
		Like | lat_d =   6 | lat_m =  5 | lat_s = | lat_NS = N
		'''
		dimParts = dimension.split('|')
		pprint(dimParts)
		degrees = nonDigitsPattern.sub('',dimParts[0])
		print dimParts[0]
		try:
			dimFloat = float(degrees)
		except ValueError:
			raise PageProcessorException("Lat/Lng in infobox but not filled in")

		#pdb.set_trace()

		for part in dimParts[1:]:
			if '_m' in part:
				minuteParts = part.split('=')
				if len(minuteParts)>=2:
					minutes = minuteParts[1]
					minutes = nonDigitsPattern.sub('',minutes)
					if minutes:
						dimFloat += float(minutes)/60.0
			if '_s' in part:
				secondParts = part.split('=')
				if len(secondParts)>=2:
					seconds = secondParts[1]
					seconds = nonDigitsPattern.sub('',seconds)
					if seconds:
						dimFloat += float(seconds)/3600.0
			if '_NS' in part:
				if part.split('=')[1].strip() == 'S' and dimFloat>0:
					dimFloat *= -1.0
			if '_EW' in part:
				if part.split('=')[1].strip() == 'W' and dimFloat>0:
					dimFloat *= -1.0
		return dimFloat