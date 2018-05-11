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
def addDictionary(cmap,fontDict):
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
def getTextSection(document):
	textStart=document.find('BT')+len('BT')
	textEnd=document.find('ET')
	textSection=document[textStart:textEnd].split('\n')
	return textSection
def getTokens(document):
	tokens=[]
	for line in document:
		if line.find('TJ')>=0:
			start=line.find('[')+1
			end=line.rfind(']')
			token=line[start:end].split(' ')
			tokens.append(token)
	return tokens
def getCodes(token):
	codes=[]
	n=len(token)
	i=0
	while i<n:
		codes+=[token[i:i+4]]
		i+=4
	return codes
def translate(tokens,fontDict):
	text=''
	for line in tokens:
		for token in line:
			if token[0]=='<':
				codes=getCodes(token.strip('<>'))
				for code in codes:
					x=int(code,base=16)
					if x in fontDict:
						if fontDict[x] in range(256):
							letter=chr(fontDict[x])
						else:
							letter='*'
						text+=letter
					else:
						text+='?'
			else:
				text+='#'
	return text
fp=open('Melvin-Lim.pdf')
codes=getAll(fp)
for i in codes[2].split('\n'):
	print i
for i in codes[6].split('\n'):
	print i
fontDict=dict()
cmap=codes[6]
fontDict=addDictionary(cmap,fontDict)
cmap=codes[9]
fontDict=addDictionary(cmap,fontDict)
document=codes[2]
textSection=getTextSection(document)
tokens=getTokens(textSection)
text=translate(tokens,fontDict)
print text
