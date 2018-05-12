class Obj():
	def __init__(self,objN,genN,raw):
		self.objN=objN
		self.genN=genN
		data=raw.strip('<<')
		data=data.split('>>')
		self.params=data[0].split('\n')
		self.data=[]
		if len(data)>1:
			for words in data[1:]:
				tmp=words.strip('\n')
				if tmp!='':
					self.data.append(tmp)
