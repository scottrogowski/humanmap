def extractBetween(string,delimiterA,delimiterB,startAt=0):
	'''
	Extract the text from between two delimiters
	'''
	string = string[startAt:]
	delimSize = len(delimiterA)
	if delimSize != len(delimiterB):
		raise Exception("delimiterA must be the same length as delimiterB")

	start = string.find(delimiterA)+delimSize

	if start == -1:
		return ''

	count = 1
	i = start
	while i<len(string) and count>0:
		tmp = string[i:i+delimSize]
		if tmp==delimiterA:
			count += 1
			i+=delimSize
		elif tmp==delimiterB:
			count -= 1
			i+=delimSize
		else:
			i+=1

	if count==0:
		return string[start:i-delimSize]
	else:
		return ''




