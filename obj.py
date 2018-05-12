def extractTokens(raw):
	start=raw.find('<<')+2
	end=raw.rfind('>>')
	if start<0 or end<0:
		return raw
	tmp=raw[start:end]
	return tmp
class Obj():
	def __init__(self,objN,genN,raw):
		self.objN=int(objN)
		self.genN=int(genN)
		params=extractTokens(raw)
		paramEnd=raw.rfind('>>')
		if paramEnd>=0:
			paramEnd+=2
			data=raw[paramEnd:]
		else:
			data=''
		self.params=dict()
		self.isFontTable=False
		self.isPage=False
		for words in params.split('\n'):
			tmp=words.split(' ')
			tmp=filter(None,tmp)
			if len(tmp)>1:
				self.params[tmp[0]]=tmp[1:]
		fontIndex=params.find('/Font')
		if fontIndex>=0:
			fontIndex+=5
			tmp=params[fontIndex:].replace('\n',' ')
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
		filterIndex=params.find('/Filter')
		if filterIndex>=0:
			tmp=params[filterIndex:].split('\n')
			tmp=tmp[0]
			tmp=tmp.split(' ')
			if len(tmp)>1:
				self.params[tmp[0]]=tmp[1:]
		self.stream=[]
		self.isText=False
		self.isCMap=False
		if data!='' and data!='\n':
			tmp=data
			if tmp.find('endstream')>=0:
				tmp=tmp.strip('\n')
				tmp=tmp.strip('endstream')
				tmp=tmp.strip('stream')
				tmp=tmp.strip('\n')
			if '/Filter' in self.params and '/FlateDecode' in self.params['/Filter']:
				import zlib
				try:
					self.stream=zlib.decompress(tmp)
				except:
					print 'zlib failed header check'
					self.stream=[]
			else:
				self.stream=tmp
		else:
			self.stream=[]
		if self.stream!=[]:
			if self.stream.find('BT')>=0 and self.stream.find('ET')>=0:
				self.isText=True
			elif self.stream.find('CMap')>=0:
				self.cmap=self.getDictionary()
				self.isCMap=True
		if '/Type' in self.params and '/Page' in self.params['/Type']:
			self.isPage=True
		if '/Page' in self.params:
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
