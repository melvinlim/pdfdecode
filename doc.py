from obj import Obj
class Doc():
	def __init__(self,fp):
		self.objs=self.getAllObjects(fp)
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
