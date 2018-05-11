import zlib
def findNextStream(fp):
	line=fp.readline()
	while line!='' and line.strip()!='stream':
		line=fp.readline()
def getNextStream(fp):
	findNextStream(fp)
	code=''
	line=fp.readline()
	while line!='' and line.strip()!='endstream':
		code+=line
		line=fp.readline()
	try:
		code=zlib.decompress(code)
	except:
		return code
	return code
def getAll(fp):
	codes=[]
	code=getNextStream(fp)
	while code!='':
		codes.append(code)
		code=getNextStream(fp)
	return codes
def getDictionary(cmap):
	fontDict=dict()
	bfcStart=cmap.find('beginbfchar')+len('beginbfchar')
	bfcEnd=cmap.find('endbfchar')
	bfchars=cmap[bfcStart:bfcEnd].split('\n')
	for line in bfchars:
		pair=line.split(' ')
		if len(pair)==2:
			srcCode=int(pair[0].strip('<>'),base=16)
			dstString=int(pair[1].strip('<>'),base=16)
			fontDict[srcCode]=dstString
	return fontDict
fp=open('Melvin-Lim.pdf')
codes=getAll(fp)
for i in codes[2].split('\n'):
	print i
for i in codes[6].split('\n'):
	print i
cmap=codes[6]
fontDict=getDictionary(cmap)
