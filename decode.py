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
		elif line.find('Tf')>=0:
			token=[line.split(' ')[0]]
#			token=[line]
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
def translate(tokens,cmaps):
	text=''
	fontDict=cmaps[0]
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
			elif token[0]=='/':
				text+='['+token+']'
				if token[2:4]=='15':
					print token[2:4]
					fontDict=cmaps[1]
				else:
					print token[2:4]
					fontDict=cmaps[0]
			else:
				text+='#'
	return text
def getCMaps(codes):
	cmaps=[]
	for section in codes:
		if section.find('beginbf')>=0:
			fontDict=getDictionary(section)
			cmaps.append(fontDict)
	return cmaps
def getTextSections(codes):
	ts=[]
	for section in codes:
		if section.find('BT')>=0 and section.find('ET')>=0:
			textSection=getTextSection(section)
			ts.append(textSection)
	return ts
fp=open('Melvin-Lim.pdf')
codes=getAll(fp)
for i in codes[2].split('\n'):
	print i
for i in codes[6].split('\n'):
	print i
cmaps=getCMaps(codes)
ts=getTextSections(codes)
text=''
for s in ts:
	tokens=getTokens(s)
	text+=translate(tokens,cmaps)
print text
