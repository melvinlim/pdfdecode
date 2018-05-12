from obj import Obj
class Doc():
	def __init__(self,fp):
		self.objs=self.getAllObjects(fp)
		self.pages=self.getPages()
	def getAllObjects(self,fp):
		objs=[]
		obj=self.getNextObj(fp)
		while obj!='':
			objs.append(obj)
			obj=self.getNextObj(fp)
		return objs
	def findNext(self,fp,identifier):
		line=fp.readline()
		while line!='' and line.find(identifier)<0:
			line=fp.readline()
		return line
	def getNextObj(self,fp):
		line=self.findNext(fp,'obj')
		while line.strip()!='obj' and len(line.split(' '))!=3 and line!='':
			line=self.findNext(fp,'obj')
		objN=-1
		genN=-1
		header=line.split(' ')
		if len(header)==3:
			objN=int(header[0])
			genN=int(header[1])
		endMarker='endobj'
		raw=''
		line=fp.readline()
		while line!='' and line.strip()!=endMarker:
			raw+=line
			line=fp.readline()
		if raw=='':
			return ''
		obj=Obj(objN,genN,raw)
		return obj
	def getObjN(self,n):
		for o in self.objs:
			if o.objN==n:
				return o
		return 0
	def getCMapObjs(self):
		ret=[]
		for o in self.objs:
			if o.isCMap:
				ret.append(o)
		return ret
	def getTextObjs(self):
		ret=[]
		for o in self.objs:
			if o.isText:
				ret.append(o)
		return ret
	def getPages(self):
		ret=[]
		for o in self.objs:
			if o.isPage:
				ret.append(o)
		return ret
	def display(self):
		self.fontMap=dict()
#		print pages
		for page in self.pages:
			contents=''
			if '/Contents' in page.params:
				tmp=self.getObjN(int(page.params['/Contents'][0]))
				if tmp!=0:
					#print tmp.stream
					contents=tmp.stream
			if '/Resources' in page.params:
				if page.params['/Resources'][2]=='R':
					tmp=self.getObjN(int(page.params['/Resources'][0]))
					#print tmp
					if '/Font' in tmp.params:
						#print tmp.params['/Font']
						for font in tmp.params['/Font']:
							fontInfo=tmp.params['/Font'][font]
							cmap=0
							if fontInfo[2].strip('\n')=='R':
								#print fontInfo[0]
								fontInfo=self.getObjN(int(fontInfo[0]))
								cmap=self.getObjN(int(fontInfo.params['/ToUnicode'][0])).cmap
							self.fontMap[font]=cmap
			#print self.fontMap
			ts=self.getTextSection(contents)
			cmaps=[]
			tmp=self.getCMapObjs()
			for o in tmp:
				cmaps.append(o.cmap)
			tokens=self.getTokens(ts)
			#print tokens
			tmp=self.translate(tokens,cmaps)
			print tmp
		#tmp=self.getCMapObjs()
		#for x in tmp:
		#	print x.cmap
	def getTextSection(self,document):
		textStart=document.find('BT')+len('BT')
		textEnd=document.find('ET')
		textSection=document[textStart:textEnd].split('\n')
		return textSection
	def getTokens(self,document):
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
	def getCodes(self,token):
		codes=[]
		n=len(token)
		i=0
		while i<n:
			codes+=[token[i:i+4]]
			i+=4
		return codes
	def translate(self,tokens,cmaps):
		text=''
		fontDict=cmaps[0]
		for line in tokens:
			for token in line:
				if token[0]=='<':
					codes=self.getCodes(token.strip('<>'))
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
						#print token[2:4]
						fontDict=cmaps[1]
					else:
						#print token[2:4]
						fontDict=cmaps[0]
				else:
					text+='#'
		return text
