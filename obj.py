import re
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
class Obj(dict):
	def extractDictionary(self,words):
		n=len(words)
		i=0
		while i<n:
			key=words[i]
			if len(key)>0 and key[0]=='/':
				value=words[i+1]
				if value.find('<<')>=0:
					start=i+2
					i+=1
					while i<n and value.find('>>')<0:
						i+=1
						value=words[i]
					end=i
					self[key]=self.extractDictionary(words[start:end])
	#				print '************************'
	#				print words[start:end]
	#				print self[key]
	#				print '************************'
					#self[key]=tmp
				elif value.find('(')>=0:
					tmp=[]
					i+=1
					tmp.append(words[i])
					while i<n and value.find(')')<0:
						i+=1
						value=words[i]
						tmp.append(value)
					self[key]=tmp
				elif value.find('[')>=0:
					tmp=[]
					i+=1
					tmp.append(words[i])
					while i<n and value.find(']')<0:
						i+=1
						value=words[i]
						tmp.append(value)
					self[key]=tmp
				elif value!='' and re.match(r'[0-9]+',value):
					if (i+3)<n:
						values=value
						if words[i+3][0]=='R':
							values=words[i+1:i+4]
						self[key]=values
						i+=4
					if key not in self:
						self[key]=value
						i+=2
				else:
					self[key]=value
					i+=2
			else:
				i+=1
	def __init__(self,objN,genN,raw):
		self.objN=int(objN)
		self.genN=int(genN)
		self.stream=extractStream(raw)
		rawDictionary=extractRawDictionary(raw)
		tmp=re.sub(r'[\n\r ]+',' ',raw)
		tmp.strip(' ')
		words=tmp.split(' ')
		self.extractDictionary(words)
		self.isFontTable=False
		self.isPage=False
		self.isText=False
		self.isCMap=False
		if '/Filter' in self and '/FlateDecode' in self['/Filter']:
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
		if '/Type' in self and '/Page' in self['/Type']:
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
