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
		x=extractTokens(raw)
		data=raw.strip('<<')
		data=data.strip('\n')
		data=data.split('>>')
		params=data[0].split('\n')
		self.params=dict()
		self.isFontTable=False
		self.isPage=False
		fontIndex=data[0].find('/Font')
		if fontIndex>=0:
			tmp=data[0][fontIndex:]
			if tmp.find('<<')>=0:
#				print tmp.split(' ')
				if tmp.split(' ')[1].strip('\n')=='<<':
					tmp=extractTokens(tmp)
					print fontIndex
					print tmp
					tmp=tmp.split(' ')
					n=len(tmp)
					i=0
					while(i<n):
						self.params[tmp[i]]=tmp[i+1:i+4]
						i+=4
					self.isFontTable=True
		filterIndex=data[0].find('/Filter')
		if filterIndex>=0:
			tmp=data[0][filterIndex:].split('\n')
			tmp=tmp[0]
			tmp=tmp.split(' ')
			if len(tmp)>1:
				self.params[tmp[0]]=tmp[1:]
		for words in params:
			tmp=words.split(' ')
			tmp=filter(None,tmp)
			if len(tmp)>1:
				self.params[tmp[0]]=tmp[1:]
		self.data=[]
		self.isText=False
		self.isCMap=False
		if len(data)==2 and data[1]!='' and data[1]!='\n':
			tmp=data[1]
			if tmp.find('endstream')>=0:
				tmp=tmp.strip('\n')
				tmp=tmp.strip('endstream')
				tmp=tmp.strip('stream')
				tmp=tmp.strip('\n')
			if '/Filter' in self.params and '/FlateDecode' in self.params['/Filter']:
				import zlib
				try:
					self.data=zlib.decompress(tmp)
				except:
					print 'zlib failed header check'
					self.data=[]
			else:
				self.data=tmp
		else:
			self.data=[]
		if self.data!=[]:
			if self.data.find('BT')>=0 and self.data.find('ET')>=0:
				self.isText=True
			elif self.data.find('CMap')>=0:
				self.cmap=self.getDictionary()
				self.isCMap=True
		if '/Type' in self.params and '/Page' in self.params['/Type']:
			self.isPage=True
		if '/Page' in self.params:
			self.isPage=True
	def getDictionary(self):
		if self.data==[]:
			return
		cmap=self.data
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
			print bfrange
			for line in bfrange:
				triple=line.split(' ')
				if len(triple)==3:
					print triple
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
