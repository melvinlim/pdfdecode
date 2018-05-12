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
		if identifier=='stream':
			if line.strip()!='stream':
				while line!='' and line.strip()!='stream':
					line=fp.readline()
	def getNextObj(self,fp):
		identifier='obj'
		line=self.findNext(fp,identifier)
		while line.strip()!='obj' and len(line.split(' '))!=3 and line!='':
			line=self.findNext(fp,identifier)
		objN=-1
		genN=-1
		header=line.split(' ')
		if len(header)==3:
			objN=header[0]
			genN=header[1]
		endMarker='end'+identifier
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
#		print pages
		for page in self.pages:
			if '/Contents' in page.params:
				tmp=self.getObjN(int(page.params['/Contents'][0]))
				if tmp!=0:
					print tmp.data
			if '/Resources' in page.params:
				if page.params['/Resources'][2]=='R':
					tmp=self.getObjN(int(page.params['/Resources'][0]))
					print tmp
					if '/Font' in tmp.params:
						asdf=0
						print tmp.params['/Font']
		tmp=self.getCMapObjs()
		for x in tmp:
			print x.cmap
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
