import re
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
def getBalanced(name,left,right,s,e,raw):
	p=1
	s+=len(left)
	for i in range(s,e):
		if raw[i:i+len(left)]==left:
			p+=1
		elif raw[i:i+len(left)]==right:
			p-=1
			if p==0:
				return (s,i,name)
	return (None,None,None)
def getToken(s,e,raw):
	for i in range(s,e):
		if raw[i]=='<':
			return getBalanced('dictionary','<<','>>',i,e,raw)
		elif raw[i]=='[':
			return getBalanced('array','[',']',i,e,raw)
		elif raw[i]=='(':
			return getBalanced('string','(',')',i,e,raw)
		elif raw[i]=='/':
			rex=re.search('^/[a-zA-Z]+[0-9]*',raw[i:e])
			if rex:
				s=i+rex.start()
				e=i+rex.end()
				return (s,e,'name')
		elif raw[i] in '0123456789':
			rex=re.search('^[0-9]+ [0-9]+ R',raw[i:e])
			if rex:
				return (i+rex.start(),i+rex.end(),'pointer')
			rex=re.search('^[0-9]+',raw[i:e])
			if rex:
				return (i+rex.start(),i+rex.end(),'number')
		else:
			rex=re.search('^([/a-zA-Z0-9:.-]+[ ]*)+',raw[i:e])
			if rex:
				return (i+rex.start(),i+rex.end(),'misc')
	return (None,None,None)
class Obj(dict):
	def extDict(self,raw):
		n=len(raw)
		s,e,t=getToken(0,n,raw)
		key=None
		while e:
			token=raw[s:e]
			print self.objN,self.genN,s,e,t,token
			if key:
				if t=='name':
					value=token
				else:
					value=Obj(-1,-1,token)
				self[key]=value
				key=None
				print '*********************************'
			elif t=='name':
				key=token
			elif t in ['number','pointer','misc']:
				self[t]=token
			else:
				value=Obj(-1,-1,token)
				self[t]=value
			s,e,t=getToken(e,n,raw)
	def __init__(self,objN,genN,raw):
		self.objN=int(objN)
		self.genN=int(genN)
		self.stream=extractStream(raw)
		s=raw.find('stream')
		e=raw.find('endstream')
		tmp=raw[:s]+raw[e+9:]
		if s>=0 and e>=0 and e>s:
			self.filtered=tmp
		else:
			self.filtered=raw
		self.raw=raw
		self.extDict(self.filtered)
		self.isPage=False
		self.isText=False
		self.isCMap=False
		if 'dictionary' in self and '/Filter' in self['dictionary']:
			if '/FlateDecode' in self['dictionary']['/Filter']:
				import zlib
				self.rawStream=self.stream
				try:
					self.stream=zlib.decompress(self.stream,0)
				except:
					print 'zlib failed header check'
					self.stream=[]
			else:
				print self['dictionary']['/Filter']
#				assert False
		if self.stream!=[]:
			if self.stream.find('BT')>=0 and self.stream.find('ET')>=0:
				self.isText=True
#			elif self.stream.find('CMap')>=0:
#				self.cmap=self.getDictionary()
#				self.isCMap=True
		if 'dictionary' in self and '/Type' in self['dictionary']:
			if self['dictionary']['/Type']=='/Page':
				self.isPage=True
	def getDictionary(self):
		#assert self.stream!=[]
		if self.stream==[]:
			return []
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
