import re
def extractDictionary(words):
	result=dict()
	n=len(words)
	i=1
	while i<n:
		key=words[i]
		if len(key)>0 and key[0]=='/':
			value=words[i+1]
			if value.find('<<')>=0:
				i+=1
				tmp=[]
				while i<n and value.find('>>')<0:
					i+=1
					value=words[i]
					tmp.append(value)
				result[key]=tmp
			elif value.find('(')>=0:
				result[key]='string'
				i+=1
				while i<n and value.find(')')<0:
					i+=1
					value=words[i]
			elif value.find('[')>=0:
				result[key]='array'
				i+=1
				while i<n and value.find(']')<0:
					i+=1
					value=words[i]
			elif value!='' and re.match(r'[0-9]+',value):
				if (i+3)<n:
					values=value
					if words[i+3][0]=='R':
						values=words[i+1:i+4]
					result[key]=values
					i+=4
				if key not in result:
					result[key]=value
					i+=2
			else:
				result[key]=value
				i+=2
		else:
			i+=1
	return result
def extractRawDictionary(raw):
	start=raw.find('<<')
	end=raw.rfind('>>')
	if start<0 or end<0:
		return ''
	tmp=raw[start+2:end]
	tmp=tmp.strip('\n')
	tmp=tmp.strip('\r')
	tmp=tmp.strip('\n')
	return tmp
def extractStream(raw):
	start=raw.find('stream')
	end=raw.rfind('endstream')
	if start<0 or end<0:
		return []
	stream=raw[start+6:end]
	stream=stream.strip('\n')
	stream=stream.strip('\r')
	stream=stream.strip('\n')
	return stream
class Obj():
	def __init__(self,objN,genN,raw):
		self.objN=int(objN)
		self.genN=int(genN)
		self.stream=extractStream(raw)
		rawDictionary=extractRawDictionary(raw)
		tmp=re.sub(r'[\n\r ]+',' ',raw)
		tmp.strip(' ')
		words=tmp.split(' ')
		self.params=extractDictionary(words)
		print self.params
		self.isFontTable=False
		self.isPage=False
		fontIndex=rawDictionary.find('/Font')
		if fontIndex>=0:
			fontIndex+=5
			tmp=rawDictionary[fontIndex:].replace('\n',' ')
			if tmp[0:4]!='Desc':
				nextIndex=tmp.find('<<')
				if nextIndex>=0:
					nextIndex+=2
					tmp=tmp[nextIndex:]
					tmp=tmp.split(' ')
					t=0
					for word in tmp:
						if word.strip('\n')=='>>':
							end=t
							break
						t+=1
					tmp=tmp[:t]
					tmp=filter(None,tmp)
#					print fontIndex
#					print tmp
					n=len(tmp)
					i=0
					self.params['/Font']=[]
					while i<n and tmp[i][0:2]=='/F':
						self.params[tmp[i]]=tmp[i+1:i+4]
#						print self.params[tmp[i]]
						self.params['/Font'].append(tmp[i])
						i+=4
					self.isFontTable=True
		self.isText=False
		self.isCMap=False
		if '/Filter' in self.params and '/FlateDecode' in self.params['/Filter']:
			import zlib
			try:
				self.stream=zlib.decompress(self.stream)
			except:
				print 'zlib failed header check'
				self.stream=[]
		if self.stream!=[]:
			if self.stream.find('BT')>=0 and self.stream.find('ET')>=0:
				self.isText=True
			elif self.stream.find('CMap')>=0:
				self.cmap=self.getDictionary()
				self.isCMap=True
		if '/Type' in self.params and '/Page' in self.params['/Type']:
			self.isPage=True
	def getDictionary(self):
		assert self.stream!=[]
		cmap=self.stream
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
		bfrStart=cmap.find('beginbfrange')+len('beginbfrange')
		bfrEnd=cmap.find('endbfrange')
		if bfrStart>=0 and bfrEnd>0:
			bfrange=cmap[bfrStart:bfrEnd].split('\n')
#			print bfrange
			for line in bfrange:
				triple=line.split(' ')
				if len(triple)==3:
#					print triple
					if triple[2][0]=='[':
						pair=0
					else:
						pair=triple[0:2]
						start=int(pair[0].strip('<>'),base=16)
						end=int(pair[1].strip('<>'),base=16)
					srcCode=start
					offset=int(triple[2].strip('<>'),base=16)
					while srcCode<=end:
						fontDict[srcCode]=offset
						srcCode+=1
						offset+=1
		return fontDict
